import os

import sublime
import sublime_plugin


class EePrependModCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.validate_file_extension()

        if self.is_prepended_module_file_opened():
            original_filepath = self.view.file_name().replace('ee', '')
            return self.view.window().open_file(original_filepath)

        self.set_prepended_module_path()
        self.set_klass_name()

        if not self.is_prepend_mod_line_exist():
            self.add_prepend_mod_line(edit)

        if not os.path.exists(self.prepended_module_path):
            create_file(self.prepended_module_path, self.build_prepended_module_skeleton())

        self.view.window().open_file(self.prepended_module_path)

    # Setters

    def set_prepended_module_path(self):
        original_path = self.view.file_name()
        paths = original_path.split('/')

        try:
            split_folder_index = paths.index('app')
            split_folder_name = 'app'
        except ValueError:
            split_folder_index = paths.index('lib')
            split_folder_name = 'lib'

        root_path = '/'.join(paths[:split_folder_index] + [f'ee/{split_folder_name}/'])

        if split_folder_name == 'app':
            if 'concerns' in paths:
                self.prepended_module_path = root_path + '/'.join(paths[split_folder_index + 1:-1] + ['ee', paths[-1]])
            else:
                self.prepended_module_path = root_path + '/'.join([paths[split_folder_index + 1], 'ee'] + paths[split_folder_index + 2:])
        else:
            self.prepended_module_path = root_path + '/'.join(['ee'] + paths[split_folder_index + 1:])

    def set_klass_name(self):
        # Finds <klass_path> start index from string (ee/.../ee/<klass_path>)
        start_index = self.prepended_module_path.rindex('ee') + 2
        # Filepath has extension `.rb`
        end_index = self.prepended_module_path.index('.')

        klass_path = self.prepended_module_path[start_index:end_index]
        # Camelize & glue together with `::`
        self.klass_name = klass_path.title().replace('_', '').replace('/', '::')[2:]

    # Actions

    def add_prepend_mod_line(self, edit):
        self.view.insert(edit, self.view.size(), f"\n{self.klass_name}.prepend_mod")
        self.view.run_command('save')

    # Helper methods

    def validate_file_extension(self):
        if not '.rb' in self.view.file_name():
            raise ValueError('Not ruby file')

        if 'ee' in self.view.file_name() and not self.is_prepended_module_file_opened():
            raise ValueError('Not prepened module path')

    def is_prepended_module_file_opened(self):
        return self.view.file_name().count('ee') == 2

    def is_prepend_mod_line_exist(self):
        last_line_number = self.view.rowcol(self.view.size())[0]

        prelast_line_point = self.view.text_point(last_line_number - 1, 0)
        prelast_line_region = self.view.line(prelast_line_point)
        prelast_line_content = self.view.substr(prelast_line_region)

        return 'prepend_mod' in prelast_line_content

    def build_prepended_module_skeleton(self):
        skeleton = '# frozen_string_literal: true\n\n'
        namespaces = ['EE'] + self.klass_name.split('::')
        indent = 0

        for namespace in namespaces:
            skeleton += f"{indent * ' '}module {namespace}\n"
            indent += 2

        skeleton += f"{indent * ' '}extend ::Gitlab::Utils::Override\n"

        while indent != 0:
            indent -= 2
            skeleton += f"{indent * ' '}end\n"

        return skeleton

def create_file(filename, data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w') as file:
        file.write(data)

