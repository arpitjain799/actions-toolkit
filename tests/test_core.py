import io
import os
import sys

from actions_toolkit import core
from actions_toolkit.utils import to_command_properties, AnnotationProperties

test_env_vars = {
    'my var': '',
    'special char var \r\n];': '',
    'my var2': '',
    'my secret': '',
    'special char secret \r\n];': '',
    'my secret2': '',
    'PATH': f'path1${os.pathsep}path2',

    # Set inputs
    'INPUT_MY_INPUT': 'val',
    'INPUT_MISSING': '',
    'INPUT_SPECIAL_CHARS_\'\t"\\': '\'\t"\\ response ',
    'INPUT_MULTIPLE_SPACES_VARIABLE': 'I have multiple spaces',
    'INPUT_BOOLEAN_INPUT': 'true',
    'INPUT_BOOLEAN_INPUT_TRUE1': 'true',
    'INPUT_BOOLEAN_INPUT_TRUE2': 'True',
    'INPUT_BOOLEAN_INPUT_TRUE3': 'TRUE',
    'INPUT_BOOLEAN_INPUT_FALSE1': 'false',
    'INPUT_BOOLEAN_INPUT_FALSE2': 'False',
    'INPUT_BOOLEAN_INPUT_FALSE3': 'FALSE',
    'INPUT_WRONG_BOOLEAN_INPUT': 'wrong',
    'INPUT_WITH_TRAILING_WHITESPACE': '  some val  ',

    'INPUT_MY_INPUT_LIST': 'val1\nval2\nval3',

    # Save inputs
    'STATE_TEST_1': 'state_val',

    # File Commands
    'GITHUB_PATH': '',
    'GITHUB_ENV': ''
}

for k, v in test_env_vars.items():
    os.environ[k] = v


def call(func, *args, **kw):
    output = io.StringIO()
    sys.stdout = output
    func(*args, **kw)
    sys.stdout = sys.__stdout__
    return output.getvalue()


assert core.get_input('my input') == 'val'

assert core.get_input('my input', required=True) == 'val'

try:
    core.get_input('missing', required=True)
except Exception as e:
    assert str(e) == 'Input required and not supplied: MISSING'
else:
    raise Exception('Expected raise Exception but it did not')

assert core.get_input('missing', required=False) == ''

assert core.get_input('My InPuT') == 'val'

assert core.get_input('special chars_\'\t"\\') == '\'\t"\\ response'

assert core.get_input('multiple spaces variable') == 'I have multiple spaces'

assert core.get_multiline_input('my input list') == ['val1', 'val2', 'val3']

assert core.get_input('with trailing whitespace') == 'some val'

assert core.get_input('with trailing whitespace', trim_whitespace=True) == 'some val'

assert core.get_input('with trailing whitespace', trim_whitespace=False) == '  some val  '

assert core.get_boolean_input('boolean input') is True

assert core.get_boolean_input('boolean input', required=True) is True

assert core.get_boolean_input('boolean input true1') is True
assert core.get_boolean_input('boolean input true2') is True
assert core.get_boolean_input('boolean input true3') is True
assert core.get_boolean_input('boolean input false1') is False
assert core.get_boolean_input('boolean input false2') is False
assert core.get_boolean_input('boolean input false3') is False

try:
    core.get_boolean_input('wrong boolean input')
except Exception as e:
    assert str(e) == 'Input does not meet YAML 1.2 "Core Schema" specification: wrong boolean input\n' \
                     'Support boolean input list: `true | True | TRUE | false | False | FALSE`'
else:
    raise Exception('Expected raise Exception but it did not')

assert call(core.set_output, 'some output', 'some value') == \
       f'{os.linesep}::set-output name=some output::some value{os.linesep}'

assert call(core.set_output, 'some output', False) == f'{os.linesep}::set-output name=some output::false{os.linesep}'

assert call(core.set_output, 'some output', 1.01) == f'{os.linesep}::set-output name=some output::1.01{os.linesep}'

assert call(core.error, 'Error message') == f'::error::Error message{os.linesep}'

assert call(core.error, 'Error message\r\n\n') == f'::error::Error message%0D%0A%0A{os.linesep}'

message = 'this is my error message'
error = Exception(message)
assert call(core.error, error) == f'::error::Error: {message}{os.linesep}'

assert call(core.error, error, title='A title', file='root/test.txt',
            start_column=1, end_column=2, start_line=5, end_line=5) == \
       f'::error title=A title,file=root/test.txt,line=5,endLine=5,col=1,endColumn=2::Error: {message}{os.linesep}'

assert call(core.warning, 'Warning') == f'::warning::Warning{os.linesep}'

assert call(core.warning, '\r\nwarning\n') == f'::warning::%0D%0Awarning%0A{os.linesep}'

assert call(core.warning, error) == f'::warning::Error: {message}{os.linesep}'

assert call(core.warning, error, title='A title', file='root/test.txt',
            start_column=1, end_column=2, start_line=5, end_line=5) == \
       f'::warning title=A title,file=root/test.txt,line=5,endLine=5,col=1,endColumn=2::Error: {message}{os.linesep}'

assert call(core.notice, '\r\nnotice\n') == f'::notice::%0D%0Anotice%0A{os.linesep}'

assert call(core.notice, error) == f'::notice::Error: {message}{os.linesep}'

assert call(core.notice, error, title='A title', file='root/test.txt',
            start_column=1, end_column=2, start_line=5, end_line=5) == \
       f'::notice title=A title,file=root/test.txt,line=5,endLine=5,col=1,endColumn=2::Error: {message}{os.linesep}'

annotation_properties = AnnotationProperties(title='A title', file='root/test.txt', start_column=1, end_column=2,
                                             start_line=5, end_line=5)
command_properties = to_command_properties(annotation_properties)
assert command_properties['title'] == 'A title'
assert command_properties['file'] == 'root/test.txt'
assert command_properties['col'] == 1
assert command_properties['endColumn'] == 2
assert command_properties['line'] == 5
assert command_properties['endLine'] == 5
assert command_properties.get('startColumn') is None
assert command_properties.get('startLine') is None

assert call(core.start_group, 'my-group') == f'::group::my-group{os.linesep}'

assert call(core.end_group) == f'::endgroup::{os.linesep}'

assert call(core.debug, 'Debug') == f'::debug::Debug{os.linesep}'

assert call(core.save_state, 'state_1', 'some value') == f'::save-state name=state_1::some value{os.linesep}'

assert call(core.save_state, 'state_1', 1) == f'::save-state name=state_1::1{os.linesep}'

assert call(core.save_state, 'state_1', True) == f'::save-state name=state_1::true{os.linesep}'

assert core.get_state('TEST_1') == 'state_val'

os.environ.pop('RUNNER_DEBUG', None)
assert core.is_debug() is False
os.environ['RUNNER_DEBUG'] = '1'
assert core.is_debug() is True
os.environ.pop('RUNNER_DEBUG', None)

assert call(core.set_command_echo, True) == f'::echo::on{os.linesep}'

assert call(core.set_command_echo, False) == f'::echo::off{os.linesep}'
