from django.http import HttpResponse
import logging
from django.conf import settings
from datetime import datetime, timedelta
from worldometer.worldometer import GetAllCountryData
from common import const as const
from common.common import load_redis_data, save_redis_data, check_session_active,\
    handle_exception_decorator


class GetCovidSummary(GetAllCountryData):
    def __init__(self, country_name):
        super().__init__()
        self.country_name = country_name.lower()
        self.redis_data = {}
        self.Isdata = None
        self.data = None

    @handle_exception_decorator
    def get_response(self):
        self.redis_data = load_redis_data(self.country_name)
        if not self.redis_data:
            self.redis_data= load_redis_data(self.country_name)
            if not self.redis_data.get(self.country_name,None):
                _, self.redis_data[self.country_name] = self.get_data()
                # print(self.redis_data)
                # print(self.redis_data.get(self.country_name, None))
                self.redis_data['verified_session_time'] = (
                            datetime.now() + timedelta(minutes=1)).strftime(
                        const.DATE_TIME_FORMAT)
            self.redis_data['source'] = "Network Call"
            save_redis_data(self.country_name,self.redis_data)
            print(self.redis_data)
            return self.redis_data['source'], self.redis_data.get(self.country_name, None)
        else:
            valid_till = self.redis_data['verified_session_time']
            if datetime.now() <= valid_till:
                self.redis_data["source"] = "Cache"
                return self.redis_data['source'], self.redis_data.get(self.country_name, None)

            else:
                _, self.redis_data[self.country_name] = self.get_data()
                self.redis_data['verified_session_time'] = (
                        datetime.now() + timedelta(minutes=8)).strftime(
                    const.DATE_TIME_FORMAT)
                self.redis_data['source'] = "Network Call--else block"
                return self.redis_data['source'], self.redis_data.get(self.country_name, None)






        # if not check_session_active:
        #     status, self.data = self.get_data()
        #     if status == 200:
        #         self.redis_data = self.data
        #         self.redis_data['verified_session_time'] = (
        #                 datetime.now() + timedelta(minutes=8)).strftime(
        #             const.DATE_TIME_FORMAT)
        #         save_redis_data(self.country_name, self.redis_data)
        #         return self.redis_data.get(self.country_name, None)
        #
        #     else:
        #         return self.data
        # else:
        #     _, self.redis_data= self.get_data()
        #     if not self.redis_data.get(self.country_name, None):
        #         self.redis_data = load_redis_data(self.country_name)
        #         self.redis_data['verified_session_time'] = (
        #                 datetime.now() + timedelta(minutes=8)).strftime(
        #             const.DATE_TIME_FORMAT)
        #         return self.redis_data.get(self.country_name, None)
        #
        #     else:
        #         self.redis_data['verified_session_time'] = (
        #                 datetime.now() + timedelta(minutes=8)).strftime(
        #             const.DATE_TIME_FORMAT)
        #         return self.redis_data.get(self.country_name, None)



