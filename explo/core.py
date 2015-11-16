""" Main handler """
import click
import yaml
import sys
from importlib import import_module
from colorama import Fore, init

class ExploException(Exception):
    pass

class ResultException(ExploException):
    pass

@click.command()
@click.argument('filename')
def main(filename):
    """ Read file and process blocks """

    init(autoreset=True)

    try:
        fhandle = open(filename, 'r')
        content = fhandle.read()
    except IOError:
        sys.exit('could not open file %s' % filename)

    try:
        blocks = load_blocks(content)
    except yaml.YAMLError as err:
        sys.exit('error parsing document: %s' % err)

    validate_blocks(blocks)
    result = proccess_blocks(blocks)

    if result:
        print(Fore.GREEN + "===> Success")
    else:
        print(Fore.RED + "===> Failed")

def load_blocks(content):
    """ Load blocks from a YAML file """
    return [b for b in yaml.safe_load_all(content)]

def validate_blocks(blocks):
    """ Ensures minimal fields for all blocks"""

    count = 0

    for block in blocks:
        count += 1
        required_fields = ['name', 'description', 'module', 'parameter']

        if not all(k in block for k in required_fields):
            raise Exception('not all required field in block %d' % count)

def proccess_blocks(blocks):
    """ Processes all blocks """

    scope = {}
    last_result = False

    for block in blocks:
        name = block['name']
        print(Fore.YELLOW + "===> Block '%s'" % name)

        last_result, scope = module_execute(block, scope)

        if not last_result:
            return last_result

    return last_result

def module_execute(block, scope):
    """ Use corresponding module to process block """
    module = block['module']

    # dynamically load modules
    try:
        mod = import_module('explo.modules.%s' % module)
        return mod.execute(block, scope)
    except Exception as exc:
        raise Exception('[%s] module exception: %s' % (module, exc))
