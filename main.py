import json
import os
import difflib


class Schema:
    def __init__(self, path_to_schema):
        self.path_to_schema = path_to_schema
        self.schema_name = [i.split('/')[-1].split('.')[0] for i in path_to_schema]
        self.checking_event_data = {}

    def _load_event(self, path_to_event):
        file = open(path_to_event, 'r')
        self.path_to_event = path_to_event
        self.checking_event_data = json.load(file)

    def _load_schema(self, path_to_schema):
        file = open('task_folder/schema/' + path_to_schema + '.schema', 'r')
        self.scheme_data = json.load(file)

    def check_event(self, path_to_event):
        self._load_event(path_to_event)

        if not self.is_json() or self.is_empty():
            return "Not a json file or has no contents, fill file with data or remove it from folder task_folder/event"

        if 'event' not in self.checking_event_data:
            return "No event name provided, please add one"

        if self.checking_event_data['event'] not in self.schema_name:
            closest_name = difflib.get_close_matches(self.checking_event_data['event'],
                                                     ["sleep_created", "label_selected",
                                                      "cmarker_created",
                                                      "workout_created"])

            return "event name " + self.checking_event_data['event'] + " is not right" + \
                   ("", ". Did you mean " + str(*closest_name) + "?")[bool(closest_name)] + \
                    "\nСhange event_name in file or add corresponding schema to task_folder/schema folder"

        path_to_schema = [i for i in self.schema_name if i == self.checking_event_data['event']]

        self._load_schema(path_to_schema[0])

        if not self.checking_event_data['data']:
            return "data field in is not filled, please load required data"
        self.check_required(self.scheme_data, self.checking_event_data['data'])

        return "Scan is over"

    def check_required(self, schema, event_json):
        requirement_check = all(item in event_json.keys() for item in schema.get('required'))
        if not requirement_check:
            time = (event_json['timestamp'] + " timestamp ") if ('timestamp' in event_json) else event_json
            print(str(set(schema.get('required')) - set(event_json)) + " is missing in the " + str(time) + " line. "
            "\nYou can find this place with ctrl + f by fragment above and paste missing data")

        for k, v in event_json.items():
            if k not in schema['properties']:
                continue

            required_type = self.translate_type(schema['properties'][k]['type'], k)

            if v is None and None in required_type:
                continue
            elif type(v) not in required_type:
                print("'" + str(v) + "' from " + k + " is not of required type " + str(required_type))
            elif type(v) == list:
                if len(v) == 0:
                    print(k + " is empty, please load contents of this object")
                for sub_v in v:
                    self.check_required(schema['properties'][k]['items'], sub_v)

    @staticmethod
    def translate_type(type_list, k):
        result = []
        if type(type_list) is not list:
            type_list = [type_list]

        for type_string in type_list:
            if type_string == 'array':
                result.append(list)
            elif type_string == 'integer' or type_string == 'number':
                result.append(int)
                if 'id' not in k:
                    result.append(float)
            elif type_string == 'object':
                result.append(dict)
            elif type_string == 'string':
                result.append(str)
            elif type_string == 'null':
                result.append(None)
            elif type_string == 'boolean':
                result.append(bool)
            else:
                print("wrong type " + str(type_string) + " in element " + str(k))
        return result

    def is_json(self):
        try:
            dict(self.checking_event_data)
        except ValueError as e:
            return False
        except TypeError as e:
            return False
        return True

    def is_empty(self):
        try:
            if not self.checking_event_data.keys():
                return True
        except:
            return True

        return False


def main():
    new_schema = Schema(["sleep_created.schema", "label_selected.schema",
                         "cmarker_created.schema", "workout_created.schema"])
    files = ['./task_folder/event/' + f for f in os.listdir('./task_folder/event/') if
             os.path.isfile('./task_folder/event/' + f)]

    for file in files:
        print('\nReading file: ' + file)
        print(new_schema.check_event(file))


if __name__ == "__main__":
    main()
