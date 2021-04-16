from __future__ import print_function
from jproperties import Properties
import json

import time
import generic_camunda_client
from generic_camunda_client.rest import ApiException
import EmailSender


def get_configs(file_name):
    configs = Properties()
    with open(file_name, 'rb') as config_file:
        configs.load(config_file)
    items_view = configs.items()
    configs_dict = {}

    for item in items_view:
        configs_dict[item[0]] = item[1].data
    return configs_dict


def run_print_weather():
    config_dict = get_configs('CamundaAPIConfig.properties')
    fetch_and_lock_payload = {"workerId": "getWeatherPrinterWorker",
                              "maxTasks": 1,
                              "usePriority": "true",
                              "topics":
                                  [{"topicName": "PrintWeather",
                                    "lockDuration": 3,
                                    "deserializeValues": True
                                    }
                                   ]
                              }

    host = config_dict.get('BaseURL')
    configuration = generic_camunda_client.Configuration(host)

    # Enter a context with an instance of the API client
    with generic_camunda_client.ApiClient(configuration) as api_client:
        api_instance = generic_camunda_client.ExternalTaskApi(api_client)

        try:
            # api_response = api_instance.evaluate_condition(evaluation_condition_dto=evaluation_condition_dto)
            api_response = api_instance.fetch_and_lock(fetch_external_tasks_dto=fetch_and_lock_payload)
            while not api_response:
                time.sleep(5)
                api_response = api_instance.fetch_and_lock(fetch_external_tasks_dto=fetch_and_lock_payload)
                print('Fetch and lock response: ', api_response)

                if api_response:
                    break
            task_id = api_response[0].id

            city_name = api_response[0].variables.get('cityName').value
            weather = ""
            if len(api_response[0].variables) > 1:
                weather = json.dumps(api_response[0].variables.get('weather').value, indent=4, sort_keys=True)
        except ApiException as e:
            print("Exception when calling ExternalTaskApi->fetch_and_lock: %s\n" % e)
            return
        EmailSender.send_email(city_name, weather)

        try:
            complete_external_task_dto = {"workerId": "getWeatherPrinterWorker",
                                          "variables": {
                                              "weather": {"value": weather}}}  # CompleteExternalTaskDto |  (optional)
            api_response = api_instance.complete_external_task_resource(task_id,
                                                                       complete_external_task_dto=complete_external_task_dto)
        except ApiException as e:
            print("Exception when calling ExternalTaskApi->complete_external_task_resource: %s\n" % e)


if __name__ == '__main__':
    try:
        while True:
            run_print_weather()
            time.sleep(15)
    except KeyboardInterrupt:
        pass
