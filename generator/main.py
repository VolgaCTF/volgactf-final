#!/usr/bin/env python3
import base64
from ecdsa import SigningKey, NIST256p
import ipaddress
import os
import random
import string
import shlex
import subprocess
import stat
import sys
import time
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def load_vars(vars_file):
    with open(vars_file, "r") as f:
        return yaml.safe_load(f)


def get_random_str(size=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))


def prepare_context(vars_file):
    # Load variables
    context = load_vars(vars_file)
    context['volgactf']['final']['transient'] = {}

    ca_root_dir = run_cmd('mkcert -CAROOT', '.', capture_output=True).stdout.strip()
    ca_root = f"{ca_root_dir}/rootCA.pem"
    context['volgactf']['final']['transient']['ca_root'] = ca_root

    net = ipaddress.ip_network(context['volgactf']['final']['network']['cidr'])
    subnets = list(net.subnets(new_prefix=24))

    expose_ports_start = context['volgactf']['final']['expose_ports']['start']
    expose_ports_end = context['volgactf']['final']['expose_ports']['end']

    system_subnet = subnets[0]
    admin_subnet = subnets[-1]
    checker_subnet = subnets[-2]

    system_ips = list(system_subnet.hosts())
    context['volgactf']['final']['transient']['nginx'] = {'ip_address': system_ips[1]}
    context['volgactf']['final']['transient']['redis'] = {'ip_address': system_ips[2]}
    context['volgactf']['final']['transient']['postgres'] = {'ip_address': system_ips[3]}
    context['volgactf']['final']['transient']['scheduler'] = {'ip_address': system_ips[4]}

    for web_ndx in range(context['volgactf']['final']['web']['replicas']):
        context['volgactf']['final']['transient']['web-{}'.format(web_ndx + 1)] = {'ip_address': system_ips[10 + web_ndx]}

    for queue_ndx in range(context['volgactf']['final']['queue']['replicas']):
        context['volgactf']['final']['transient']['queue-{}'.format(queue_ndx + 1)] = {'ip_address': system_ips[20 + queue_ndx]}

    for stream_ndx in range(context['volgactf']['final']['stream']['replicas']):
        context['volgactf']['final']['transient']['stream-{}'.format(stream_ndx + 1)] = {'ip_address': system_ips[30 + stream_ndx]}

    admin_ips = list(admin_subnet.hosts())
    context['volgactf']['final']['transient']['proxy-admin'] = {'ip_address': admin_ips[1], 'port': expose_ports_start}
    context['volgactf']['final']['transient']['pgclient'] = {'ip_address': admin_ips[2], 'port': expose_ports_end}

    checker_ips = list(checker_subnet.hosts())
    for service_ndx, (service_name, service_details) in enumerate(context['volgactf']['final']['services'].items()):
        context['volgactf']['final']['transient']['{}-checker-ingress'.format(service_name)] = {'ip_address': checker_ips[service_ndx * 10 + 9]}
        for checker_ndx in range(service_details['checker']['replicas']):
            context['volgactf']['final']['transient']['{}-checker-{}'.format(service_name, checker_ndx + 1)] = {'ip_address': checker_ips[service_ndx * 10 + 9 + checker_ndx + 1]}

    for team_ndx, (team_name, team_details) in enumerate(context['volgactf']['final']['teams'].items()):
        team_subnet = subnets[team_ndx + 1]
        team_ips = list(team_subnet.hosts())
        context['volgactf']['final']['transient']['proxy-{}'.format(team_name)] = {'ip_address': team_ips[1], 'port': expose_ports_start + team_ndx + 1}
        context['volgactf']['final']['transient']['vulnbox-{}'.format(team_name)] = {'ip_address': team_ips[2]}

    auth_master_password = get_random_str()
    auth_checker_password = get_random_str()

    context['volgactf']['final']['transient']['auth'] = {
        'master': {
            'password': auth_master_password
        },
        'checker': {
            'password': auth_checker_password
        }
    }

    private_key = SigningKey.generate(curve=NIST256p)
    public_key = private_key.get_verifying_key()
    generator_secret = base64.urlsafe_b64encode(os.urandom(32)).decode('ascii')

    context['volgactf']['final']['transient']['flag'] = {
        'sign_key': {
            'public': public_key.to_pem().decode('ascii').strip().replace('\n', '\\n'),
            'private': private_key.to_pem().decode('ascii').strip().replace('\n', '\\n')
        },
        'generator_secret': generator_secret
    }

    context['volgactf']['final']['transient']['network'] = {
        'internal': [
            system_subnet,
            admin_subnet,
            checker_subnet
        ],
        'teams': list(map(lambda ndx: subnets[ndx + 1], range(len(context['volgactf']['final']['teams']))))
    }

    # print(context)
    return context


def render_templates(template_dir, output_dir, context):
    # Setup Jinja2 environment (Ansible-style delimiters are fine)
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )

    template_dir = Path(template_dir)
    output_dir = Path(output_dir)

    for root, _, files in os.walk(template_dir):
        rel_root = Path(root).relative_to(template_dir)
        for file in files:
            template_path = rel_root / file

            rendered = None
            if template_path.name.endswith(".j2"):
                template = env.get_template(str(template_path))
                rendered = template.render(context).encode()
            else:
                with open(Path(template_dir, template_path), "rb") as f:
                    rendered = f.read()

            if file.endswith(".j2"):
                output_filename = file[:-3]
            else:
                output_filename = file

            output_path = output_dir / rel_root / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(rendered)

            print(f"Rendered {template_path} → {output_path}")
            src_stat = (template_dir / template_path).stat()
            mode = src_stat.st_mode
            os.chmod(output_path, stat.S_IMODE(mode))


def generate_cert(output_dir, context):
    domain = context['volgactf']['final']['hostname']

    """
    Generate a TLS certificate for a given domain using mkcert.
    Requires mkcert to be installed on the system.
    """
    output_path = Path(output_dir, 'nginx', 'certs')
    output_path.mkdir(parents=True, exist_ok=True)

    cert_file = output_path / f"{domain}.pem"
    key_file = output_path / f"{domain}-key.pem"

    cmd = [
        "mkcert",
        "-cert-file", str(cert_file),
        "-key-file", str(key_file),
        domain
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Certificate created: {cert_file}, {key_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ mkcert failed: {e}")
    except FileNotFoundError:
        print("❌ mkcert not found. Please install it: https://github.com/FiloSottile/mkcert")


def run_cmd(cmd, cwd, check=True, capture_output=False):
    """Helper to run shell commands in project dir"""
    print(f"→ {cmd} (cwd={cwd})")
    return subprocess.run(
        shlex.split(cmd),
        check=check,
        capture_output=capture_output,
        text=True,
        cwd=str(cwd)
    )


def service_running(service, cwd):
    """Check if a service container is running in docker compose"""
    result = run_cmd(f"docker compose ps -q {service}", cwd, capture_output=True)
    print(f"ps -> {result}")
    cid = result.stdout.strip()
    if not cid:
        return False
    # Confirm it's actually running
    result = run_cmd(f"docker inspect -f '{{{{.State.Running}}}}' {cid}", cwd, capture_output=True)
    print(f"inspect -> {result}")
    return result.stdout.strip() == "true"


def first_init(work_dir):
    required_services = ["postgres", "redis"]
    were_running = {}

    for svc in required_services:
        already = service_running(svc, work_dir)
        were_running[svc] = already
        if not already:
            run_cmd(f"docker compose up -d {svc}", work_dir)

    time.sleep(1)
    run_cmd(f"./script/dist-frontend.sh", work_dir)
    time.sleep(1)
    run_cmd(f"./script/db-reset.sh", work_dir)
    time.sleep(1)
    run_cmd(f"./script/cli.sh competition init /opt/volgactf/final/domain/competition_init.rb", work_dir)
    time.sleep(1)

    for svc, already in were_running.items():
        if not already:
            run_cmd(f"docker compose stop {svc}", work_dir)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: render.py <template_dir> <output_dir> <vars.yml>")
        sys.exit(1)

    template_dir, output_dir, vars_file = sys.argv[1:]
    context = prepare_context(vars_file)
    render_templates(template_dir, output_dir, context)
    generate_cert(output_dir, context)
    first_init(output_dir)
