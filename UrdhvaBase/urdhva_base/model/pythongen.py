import os
from typing import List
import urdhva_base.utilities
import urdhva_base.model.helpers

databases = {
    'postgres': ['urdhva_base.postgresmodel', 'urdhva_base.postgresmodel.BasePostgresModel',
                 'urdhva_base.postgresmodel.PostgresModel', 'urdhva_base.postgrestable']
}


def generate(m):
    fbase = os.path.splitext(os.path.basename(m._tx_model_params['file']))[0]
    db = databases[m._tx_model_params['db']]

    for model in m.models:
        model.dbbase = db
        model.fbase = fbase

    _write_enum_file(m.enums, fbase)
    _write_model_file(m.models, fbase)
    _write_std_api_file(m.models, fbase)
    _write_action_files(m.models, fbase)


def _write_enum_file(enums, fbase):
    content = urdhva_base.model.helpers.EnumsFile(enums).render()
    lines = content.splitlines()
    _write_formatted_file(f"{fbase}_enum.py", lines, class_padding=True)


def _write_model_file(models, fbase):
    content = urdhva_base.model.helpers.ModelsFile(models).render()
    lines = content.splitlines()

    def formatter(line, output):
        if line.strip().startswith("class"):
            _strip_trailing_empty(output)
            if line.strip().startswith("class Config:"):
                output.extend(["", line])
            else:
                output.extend(["", "", line])
        elif line.strip() == "pass":
            _strip_trailing_empty(output)
            output.append(line)
        else:
            output.append(line)

    _write_formatted_file(f"{fbase}_model.py", lines, custom_formatter=formatter)


def _write_std_api_file(models, fbase):
    content = urdhva_base.model.helpers.StdApiFile(models).render().lstrip()
    lines = content.splitlines()

    def formatter(line, output):
        if line.strip().startswith("@router."):
            _strip_trailing_empty(output)
            output.extend(["", "", line])
        elif line.startswith("  "):
            _strip_trailing_empty(output)
            output.append(line)
        else:
            output.append(line)

    _write_formatted_file(f"{fbase}_stdapi.py", lines, custom_formatter=formatter)


def _write_action_files(models, fbase):
    for model in models:
        if not model.actions:
            continue

        action_file_name = f"{urdhva_base.utilities.snake_case(model.name)}_actions.py"
        actions_data = _read_existing_actions(action_file_name)

        new_lines = []
        for i, action in enumerate(model.actions):
            if _is_action_already_present(action, actions_data):
                continue

            action.fbase = fbase
            if i == 0:
                action.route_name = model.name.lower()

            rendered = _render_action(action, i, action_file_name)
            new_lines.extend(["", ""] + rendered)

        if new_lines:
            actions_data.extend(new_lines)
            _write_actions_to_file(action_file_name, actions_data)


def _read_existing_actions(action_file_name):
    if os.path.exists(action_file_name):
        with open(action_file_name) as f:
            return f.read().splitlines()
    return []


def _is_action_already_present(action, actions_data):
    return f"# Action {action.name.lower()}" in actions_data


def _render_action(action, index, action_file_name):
    if index == 0 and not os.path.exists(action_file_name):
        return urdhva_base.model.helpers.ActionBase(action).render().splitlines()
    return action.render().lstrip().splitlines()


def _write_actions_to_file(action_file_name, actions_data):
    with open(action_file_name, "w+") as f:
        f.write("\n".join(actions_data) + "\n")


def _write_formatted_file(file_name: str, lines: List[str], class_padding=False, custom_formatter=None):
    output = []
    for line in lines:
        if custom_formatter:
            custom_formatter(line, output)
        else:
            if line.strip().startswith("class") or (class_padding and line.strip() == "pass"):
                _strip_trailing_empty(output)
                output.extend(["", "", line])
            else:
                output.append(line)

    output = "\n".join(output).strip()
    with open(file_name, "w") as f:
        f.write(output + "\n")


def _strip_trailing_empty(output: List[str]):
    while output and not output[-1].strip():
        output.pop()
