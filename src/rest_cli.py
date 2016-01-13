"""
This script provides a nice and easy to use cli to exercise the rest api. By utilizing
akrrresclient there is no need to manually track tokens ( the client does this for you ).
It provides

An example command:
GET /resources -> GET apirest_host:apirest_port/resources
GET /tasks?resource=edge&app=bench -> GET apirest_host:apirest_port/tasks?resource=edge&app=bench
"""
from prompt_toolkit import CommandLineInterface, AbortAction, Exit
from prompt_toolkit.layout import Layout
from prompt_toolkit.line import Line
from prompt_toolkit.layout.prompt import DefaultPrompt
from prompt_toolkit.layout.menus import CompletionMenu
from prompt_toolkit.completion import Completion, Completer

from pygments.style import Style
from pygments.token import Token
from pygments.styles.default import DefaultStyle

import akrrrestclient


class RESTCompleter(Completer):
    keywords = ['GET', 'PUT', 'POST', 'DELETE', 'localhost']

    def get_completions(self, document):
        word_before_cursor = document.get_word_before_cursor()

        for keyword in self.keywords:
            if keyword.startswith(word_before_cursor):
                yield Completion(keyword, -len(word_before_cursor))


class DocumentStyle(Style):
    styles = {
        Token.CompletionMenu.Completion.Current: 'bg:#00aaaa #000000',
        Token.CompletionMenu.Completion: 'bg:#008888 #ffffff',
        Token.CompletionMenu.ProgressButton: 'bg:#003333',
        Token.CompletionMenu.ProgressBar: 'bg:#00aaaa',
    }
    styles.update(DefaultStyle.styles)


def process_request(request):
    method = request[0]
    url = request[1]
    if method not in RESTCompleter.keywords:
        raise AssertionError("Invalid method. Please provide a valid method to continue.")
    if len(url) < 1:
        raise AssertionError("Must supply a url.")

    akrrrestclient.get_token()

    if method == 'GET':
        return akrrrestclient.get(url)
    elif method == 'PUT':
        return akrrrestclient.put(url)
    elif method == 'POST':
        return akrrrestclient.post(url)
    elif method == 'DELETE':
        return akrrrestclient.delete(url)


def main():
    layout = Layout(before_input=DefaultPrompt('> '),
                    menus=[CompletionMenu()])
    line = Line(RESTCompleter())
    cli = CommandLineInterface(style=DocumentStyle, layout=layout, line=line)
    try:
        while True:
            document = cli.read_input(on_exit=AbortAction.RAISE_EXCEPTION)

            input_args = document.text.split(' ')

            if len(input_args) < 2:
                raise AssertionError("Must provide at least a method and a url")

            response = process_request(input_args)

            print 'Response:', response.json()

    except Exit:
        print 'GoodBye!'

if __name__ == '__main__':
    main()