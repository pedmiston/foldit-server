from os import environ
import ansible_vault
from unipath import Path

PROJ = Path(__file__).absolute().parent

def get_from_vault(key=None, vault_file='vars/secrets.yml'):
    try:
        ansible_vault_password_file = environ['ANSIBLE_VAULT_PASSWORD_FILE']
    except KeyError:
        raise AssertionError('Set the ANSIBLE_VAULT_PASSWORD_FILE environment variable')
    ansible_vault_password = open(ansible_vault_password_file).read().strip()
    vault = ansible_vault.Vault(ansible_vault_password)
    secrets_yaml = Path(PROJ, vault_file)
    data = vault.load(open(secrets_yaml).read())
    if key is None:
        return data
    else:
        return data.get(key)
