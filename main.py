import json
import os


class Schema:
    def __init__(self, path_to_schema):
        self.path_to_schema = path_to_schema
        self.schema_name = [i.split('/')[-1].split('.')[0] for i in path_to_schema]
        self.checking_event_data = {}

    def load_event(self, path_to_event):
        file = open(path_to_event, 'r')
        self.path_to_event = path_to_event
        self.checking_event_data = json.load(file)
        return self.checking_event_data

    def check_event(self, path_to_event):
        self.checking_event_data = self.load_event(path_to_event)
        # print("is JSON" * self.is_json())
        # print("is empty" * self.is_empty())
        if not self.is_json() or self.is_empty():
            return self.path_to_event + "\n not an json file or has no contents"

        if 'event' not in self.checking_event_data:
            return self.path_to_event + "\n no event name provided"

        if self.checking_event_data['event'] not in self.schema_name:
            return self.path_to_event + "\n event name " + self.checking_event_data['event'] + " is not right"

        path_to_schema = [i for i in self.schema_name if i == self.checking_event_data['event']]

        file = open('task_folder/schema/' + path_to_schema[0] + '.schema', 'r')
        self.scheme_data = json.load(file)

        if not self.checking_event_data['data']:
            return "data field in " + self.path_to_event + " is not filled"
        self.check_required(self.scheme_data, self.checking_event_data['data'])

        return self.path_to_event + "\n ok"

    def check_required(self, scheme, json):

        what_required = scheme['required']
        what_is = json
        if type(json) == dict:
            what_is = [json]
        for i in what_required:
            for j in what_is:
                if i not in j:
                    print(i + " is not in file")

        if type(json) == dict:
            what_is = json
        if type(what_is) == dict:
            what_is = [what_is]
        for i in what_is:
            for (k, v) in i.items():
                if type(v) != list:
                    continue
                if 'required' in scheme['properties'][k]['items']:
                    return self.check_required(scheme['properties'][k]['items'], i[k])


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
    new_schema = Schema(["sleep_created.schema", "label_selected.schema", "cmarker_created.schema", "workout_created.schema"])
    files = ['./task_folder/event/' + f for f in os.listdir('./task_folder/event/') if os.path.isfile('./task_folder/event/' + f)]
    i = 0
    for file in files:
        print(new_schema.check_event(file))
        i += 1


if __name__ == "__main__":
    main()