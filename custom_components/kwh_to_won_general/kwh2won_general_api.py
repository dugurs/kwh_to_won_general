import math
import datetime
from dateutil.relativedelta import relativedelta
import logging
_LOGGER = logging.getLogger(__name__)

# 로그의 출력 기준 설정
_LOGGER.setLevel(logging.DEBUG)
# log 출력 형식
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# log 출력
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
_LOGGER.addHandler(stream_handler)

import collections
from copy import deepcopy
def merge(dict1, dict2):
    ''' Return a new dictionary by merging two dictionaries recursively. '''
    result = deepcopy(dict1)
    for key, value in dict2.items():
        if isinstance(value, collections.abc.Mapping):
            result[key] = merge(result.get(key, {}), value)
        else:
            result[key] = deepcopy(dict2[key])
    return result


# https://cyber.kepco.co.kr/ckepco/front/jsp/CY/E/E/CYEEHP00102.jsp
# https://cyber.kepco.co.kr/ckepco/front/jsp/CY/J/A/CYJAPP000NFL.jsp


CALC_PARAMETER = {
    'F1-low': { 'basic': 6160, },
    'F1-high-A1': { 'basic': 7170, },
    'F1-high-A2': { 'basic': 8230, },
    'F1-high-B1': { 'basic': 7170, },
    'F1-high-B2': { 'basic': 8230, },

    'F2-high-A1': { 'basic': 7170, },
    'F2-high-A2': { 'basic': 8230, },
    'F2-high-B1': { 'basic': 7170, },
    'F2-high-B2': { 'basic': 8230, },
    'S-high-A1': { 'basic': 7220, },
    'S-high-A2': { 'basic': 8320, },
    'S-high-A3': { 'basic': 9810, },
    'S-high-B1': { 'basic': 6630, },
    'S-high-B2': { 'basic': 7380, },
    'S-high-B3': { 'basic': 8190, },
    'S-high-C1': { 'basic': 6590, },
    'S-high-C2': { 'basic': 7520, }, 
    'S-high-C3': { 'basic': 8090, },

    'dc': {
        'etc': {
            'a1': 16000, # 5인이상 가구,출산가구,3자녀이상 가구
            'a2': 0.3,   # 생명유지장치
            'b1': 16000, # 독립유공자,국가유공자,5.18민주유공자,장애인 
            'b2': 0.3,   # 사회복지시설
            'b3': 16000, # 기초생활(생계.의료)
            'b4': 10000, # 기초생활(주거.교육)
            'b5': 8000,  # 차사위계층
        },
        'summer': { # 6~8월
            'a1': 16000,
            'a2': 0.3,
            'b1': 20000,
            'b2': 0.3,
            'b3': 20000,
            'b4': 12000,
            'b5': 10000,
        }
    }
}

# 단가표 정규식 치환
# 찾을말
# ^경부하\t([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# ^중간부하\t([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# ^최대부하\t([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# 바꿀말
# 'S-high-': { 'section': [ [\1, \2, \3], [\4, \5, \6], [\7, \8, \9] ] },

MONTHLY_PRICE = {
    '2101': {
        'F1-low':     { 'section': [[100.7, 60.2, 87.3]] },
        'F1-high-A1': { 'section': [[110.9, 66.9, 98.6]] },
        'F1-high-A2': { 'section': [[106.9, 62.6, 93.3]] },
        'F1-high-B1': { 'section': [[108.8, 65.8, 95.6]] },
        'F1-high-B2': { 'section': [[103.5, 60.5, 90.3]] },
        'F2-high-A1': { 'section': [ [57.7, 57.7, 66.4], [108.9, 65.1, 96.8], [131.4, 76.4, 111.6] ] },
        'F2-high-A2': { 'section': [ [52.4, 52.4, 61.1], [103.6, 59.8, 91.5], [126.1, 71.1, 106.3] ] },
        'F2-high-B1': { 'section': [ [57.1, 57.1, 66.1], [105.7, 63, 93.4], [122.1, 68.4, 107.6] ] }, 
        'F2-high-B2': { 'section': [ [51.8, 51.8, 60.8], [100.4, 57.7, 88.1], [116.8, 63.1, 102.3] ] },
        'S-high-A1': { 'section': [ [56.6, 56.6, 63.6], [109.5, 79.1, 109.7], [191.6, 109.8, 167.2] ] },
        'S-high-A2': { 'section': [ [51.1, 51.1, 58.1], [104, 73.6, 104.2], [186.1, 104.3, 161.7] ] },
        'S-high-A3': { 'section': [ [50.2, 50.2, 57.5], [103.4, 72.3, 103.6], [173.7, 96, 150.5] ] },
        'S-high-B1': { 'section': [ [55, 55, 62], [107.3, 77.3, 107.3], [188.5, 107.6, 163.5] ] },
        'S-high-B2': { 'section': [ [51.2, 51.2, 58.2], [103.5, 73.5, 103.5], [184.7, 103.8, 159.7] ] },
        'S-high-B3': { 'section': [ [49.5, 49.5, 56.6], [101.8, 71.9, 101.8], [183.1, 102.2, 158] ] },
        'S-high-C1': { 'section': [ [54.5, 54.5, 61.4], [107.4, 77.4, 107], [188.3, 107.8, 163.6] ] },
        'S-high-C2': { 'section': [ [49.8, 49.8, 56.7], [102.7, 72.7, 102.3], [183.6, 103.1, 158.9] ] },
        'S-high-C3': { 'section': [ [48.7, 48.7, 55.6], [101.6, 71.6, 101.2], [182.5, 102, 157.8] ] },
    },
    '2204': {
        'F1-low':     { 'section': [[105.6, 65.1, 92.2]] },
        'F1-high-A1': { 'section': [[115.8, 71.8, 103.5]] },
        'F1-high-A2': { 'section': [[111.8, 67.5, 98.2]] },
        'F1-high-B1': { 'section': [[113.7, 70.7, 100.5]] },
        'F1-high-B2': { 'section': [[108.4, 65.4, 95.2]] },
        'F2-high-A1': { 'section': [ [62.6, 62.6, 71.3], [113.8, 70, 101.7], [136.3, 81.3, 116.5] ] },
        'F2-high-A2': { 'section': [ [57.3, 57.3, 66], [108.5, 64.7, 96.4], [131, 76, 111.2] ] },
        'F2-high-B1': { 'section': [ [62, 62, 71], [110.6, 67.9, 98.3], [127, 73.3, 112.5] ] },
        'F2-high-B2': { 'section': [ [56.7, 56.7, 65.7], [105.3, 62.6, 93], [121.7, 68, 107.2] ] },
        'S-high-A1': { 'section': [ [61.5, 61.5, 68.5], [114.4, 84, 114.6], [196.5, 114.7, 172.1] ] },
        'S-high-A2': { 'section': [ [56, 56, 63], [108.9, 78.5, 109.1], [191, 109.2, 166.6] ] },
        'S-high-A3': { 'section': [ [55.1, 55.1, 62.4], [108.3, 77.2, 108.5], [178.6, 100.9, 155.4] ] },
        'S-high-B1': { 'section': [ [59.9, 59.9, 66.9], [112.2, 82.2, 112.2], [193.4, 112.5, 168.4] ] },
        'S-high-B2': { 'section': [ [56.1, 56.1, 66.1], [108.4, 78.4, 108.4], [189.6, 108.7, 164.6] ] },
        'S-high-B3': { 'section': [ [54.4, 54.4, 61.5], [106.7, 76.8, 106.7], [188, 107.1, 162.9] ] },
        'S-high-C1': { 'section': [ [59.4, 59.4, 66.3], [112.3, 82.3, 111.9], [193.2, 112.7, 168.5] ] },
        'S-high-C2': { 'section': [ [54.7, 54.7, 61.6], [107.6, 77.6, 107.2], [188.5, 108, 163.8] ] },
        'S-high-C3': { 'section': [ [53.6, 53.6, 60.5], [106.5, 76.5, 106.1], [187.4, 106.9, 162.7] ] },
    },
    '2210': {
        'F1-low':     { 'section': [[110.5, 70, 97.1]] },
        'F1-high-A1': { 'section': [[120.7, 76.7, 108.4]] },
        'F1-high-A2': { 'section': [[116.7, 72.4, 103.1]] },
        'F1-high-B1': { 'section': [[118.6, 75.6, 105.4]] },
        'F1-high-B2': { 'section': [[113.3, 70.3, 100.1]] },
        'F2-high-A1': { 'section': [ [67.5, 67.5, 76.2], [118.7, 74.9, 106.6], [141.2, 86.2, 121.4] ] },
        'F2-high-A2': { 'section': [ [62.2, 62.2, 70.9], [113.4, 69.6, 101.3], [135.9, 80.9, 116.1] ] },
        'F2-high-B1': { 'section': [ [66.9, 66.9, 75.9], [115.5, 72.8, 103.2], [131.9, 78.2, 117.4] ] },
        'F2-high-B2': { 'section': [ [61.6, 61.6, 70.6], [110.2, 67.5, 97.9], [126.6, 72.9, 112.1] ] },
        'S-high-A1': { 'section': [ [66.4, 66.4, 73.4], [119.3, 88.9, 119.5], [201.4, 119.6, 177] ] },
        'S-high-A2': { 'section': [ [60.9, 60.9, 67.9], [113.8, 83.4, 114], [195.9, 114.1, 171.5] ] },
        'S-high-A3': { 'section': [ [60, 60, 67.3], [113.2, 82.1, 113.4], [183.5, 105.8, 160.3] ] },
        'S-high-B1': { 'section': [ [64.8, 64.8, 71.8], [117.1, 87.1, 117.1], [198.3, 117.4, 173.3] ] },
        'S-high-B2': { 'section': [ [61, 61, 68], [113.3, 83.3, 113.3], [194.5, 113.6, 169.5] ] },
        'S-high-B3': { 'section': [ [59.3, 59.3, 66.4], [111.6, 81.7, 111.6], [192.9, 112, 167.8] ] },
        'S-high-C1': { 'section': [ [64.3, 64.3, 71.2], [117.2, 87.2, 116.8], [198.1, 117.6, 173.4] ] },
        'S-high-C2': { 'section': [ [59.6, 59.6, 66.5], [112.5, 82.5, 112.1], [193.4, 112.9, 168.7] ] },
        'S-high-C3': { 'section': [ [58.5, 58.5, 65.4], [111.4, 81.4, 111], [192.3, 111.8, 167.6] ] },
    },
}


# 계약전력 5kW, 월간 100kWh 사용시 전기요금 계산, 역률(지상:71%, 진상:91%)

# 기본요금(원미만 절사) : 30,800원
# 20,864.52원 = 5kW x 6,160원 x 21일/31일
# 9,935.48원 = 5kW x 6,160원 x 10일/31일

# 역률요금(원미만 절사) : 1,416.8원
# 959.77 = { 20,864.52 x ( 90 - 71 ) x 0.2% } + { 20,864.52 x ( 95 - 91 ) x 0.2% }
# 457.03 = { 9,935.48 x ( 90 - 71 ) x 0.2% } + { 9,935.48 x ( 95 - 91 ) x 0.2% }

# 전력량요금(원미만 절사) : 9,264원
# 7,180.8원 = 68kWh x 105.6원
# 2,083.2원 = 32kWh x 65.1원

# 기후환경요금(원미만 절사) : 730원
# 496.4원 = 68kWh x 7.30원
# 233.6원 = 32kWh x 7.30원
#   * 전기요금 체계개편 적용일 전·후로 일수계산. 적용일 이후의 일수 반영

# 연료비조정액(원미만 절사) : 500원
# 340원 = 68kWh x 5.00원
# 160원 = 32kWh x 5.00원
#   * 연료비조정액은 일수계산 안 함

# 전기요금 = 기본요금 + 전력량요금 + 기후환경요금 + 연료비조정요금 + 역률요금 + 200kWh이하감액 + 필수사용량보장공제액 + 복지할인금액 + 사용량0감액
# 42,710원 = 30,800원 + 9,264원 + 730원 + 500원 + 1,416원 + 0원 + 0원 + 0원 + 0원

# 부가가치세 = 전기요금 x 10% (원미만반올림)
# 4,271원 = 42,710원 x 10%

# 전력산업기반기금 = 전기요금 x 3.7% (10원미만 절사)
# 1,580원 = 42,710원 x 3.7%

# 청구금액(전기요금계 ＋ 부가가치세 ＋ 전력산업기반기금)
# : 42,710원 ＋ 4,271원 ＋ 1,580원 ＝ 48,560원(10원미만 절사)


class kwh2won_api:
    def __init__(self, cfg):
        ret = {
            'welfareDcCfg' : 0, # 복지할인요금
            'contractKWh' : 0, # 계약전력 contractKWh
            'reactive' : 0, # 무효천력량계 Reactive Power meter
            'lagging' : 90, # 지상역률 Lagging Power Factor
            'leading' : 95, # 진상역률 Leading
            'pressure' : 'F1-low', # 용도, 수전전압
            'usekwh': 0.0001,     # 사용량

            'checkDay' : 0, # 검침일
            'today': datetime.datetime.now(),
            'checkYear':0, # 검침년
            'checkMonth':0, # 검침월
            'monthDays': 0, # 월일수
            'useDays': 0, # 사용일수
            'mm1' : {
                'yymm': '',     # 사용년월
                'season': 0, # 시즌
                'usekwh': 0,     # 사용량
                'basicWon': 0,   # 기본요금
                'factorWon': 0,   # 역률요금
                'usekwhWon': 0,     # 전력량요금
                'elecBasicDc': 0, # 필수사용량보장공제
                'diffWon': 0,    # 환경비용차감
                'climateWon': 0, # 기후환경요금
                'useDays': 0,    # 사용일수
                'welfareDc': 0,  # 복지할인
                'price': {} # 단가
            },
            'mm2' : {
                'yymm': '',     # 사용년월
                'season': 0, # 시즌
                'usekwh': 0,     # 사용량
                'basicWon': 0,   # 기본요금
                'factorWon': 0,   # 역률요금
                'usekwhWon': 0,     # 전력량요금
                'elecBasicDc': 0, # 필수사용량보장공제
                'diffWon': 0,    # 환경비용차감
                'climateWon': 0, # 기후환경요금
                'useDays': 0,    # 사용일수
                'welfareDc': 0,  # 복지할인
                'price': {} # 단가
            },
            'basicWon': 0,   # 기본요금
            'factorWon': 0,   # 역률요금
            'usekwhWon': 0,     # 전력량요금
            'diffWon': 0,    # 환경비용차감
            'climateWon': 0, # 기후환경요금
            'fuelWon': 0,    # 연료비조정액
            'elecBasicDc': 0, # 필수사용량보장공제
            'elecBasic200Dc': 0, # 200kWh이하 감액
            'welfareDc': 0,  # 복지 요금할인
            'elecSumWon': 0,     # 전기요금계
            'vat': 0, # 부가가치세
            'baseFund': 0, # 전력산업기반기금
            'total': 0, # 청구금액
        }
        ret.update(cfg)
        self._ret = ret



    # 당월 단가 찾기
    def price_find(self, yymm):
        cnt = -1
        listym = list(MONTHLY_PRICE.keys())
        for ym in listym :
            if ym <= yymm:
                cnt += 1
            else :
                break
        if cnt == -1 :
            cnt = 0
        return listym[cnt]



    # 예상 사용량
    # 사용일 = (오늘 > 검침일) ? 오늘 - 검침일 : 전달일수 - 검침일 + 오늘
    # 월일수 = (오늘 > 검침일) ? 이번달일수 : 전달일수
    # 시간나누기 = ((사용일-1)*24)+(현재시간+1)
    # 시간곱하기 = 월일수*24
    # 예측 = 에너지 / 시간나누기 * 시간곱하기
    def energy_forecast(self, energy, today=None):
        if today:
            self._ret['today'] = today
        self.calc_lengthDays() # 사용일 구하기 호출
        today = self._ret['today']
        checkMonth = self._ret['checkMonth']
        checkDay = self._ret['checkDay']
        useDays = self._ret['useDays']
        monthDays = self._ret['monthDays']

        forcest = round(energy / ((((useDays - 1) * 24) + today.hour) * 60 + today.minute + 1) * (monthDays * 24 * 60 + 1), 1)
        _LOGGER.debug(f"########### 예상사용량:{forcest}, 월길이 {monthDays}, 사용일 {useDays}, 검침일 {checkDay}, 오늘 {today.day}")
        return {
            'forcest': forcest,
            'monthDays': monthDays,
            'useDays': useDays,
            'checkMonth': checkMonth,
            'checkDay': checkDay,
            'today': today.day,
        }



    # 달의 말일
    # last_day_of_month(datetime.date(2021, 12, 1))
    def last_day_of_month(self, any_day):
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        return next_month - datetime.timedelta(days=next_month.day)



    # 전달 검침말일 구하기
    def prev_checkday(self, today):
        self._ret['today'] = today
        self.calc_lengthDays()
        d = datetime.date(self._ret['checkYear'], self._ret['checkMonth'], self._ret['checkDay'])
        return d - datetime.timedelta(days=1)



    # 월 사용일 구하기
    def calc_lengthDays(self) :
        today = self._ret['today']
        checkDay = self._ret['checkDay']
        if (checkDay == 0 or checkDay >= 28): # 검침일이 말일미면
            lastday = self.last_day_of_month(today) # 이번달 말일
            if today.day == lastday.day : # 오늘이 말일미면, 시작일
                next_lastday = self.last_day_of_month(today + datetime.timedelta(days=1)) # 다음달 말일
                checkYear = today.year
                checkMonth = today.month
                monthDays = next_lastday.day
                useDays = 1
                checkDay = today.day
            else : # 말일이 아니면
                prev_lastday = today - datetime.timedelta(days=today.day) # 전달 말일
                checkYear = prev_lastday.year
                checkMonth = prev_lastday.month
                monthDays = lastday.day
                useDays = today.day + 1
                checkDay = prev_lastday.day
        else :
            if today.day >= checkDay : # 오늘이 검침일보다 크면
                lastday = self.last_day_of_month(today) # 달의 마지막일이 전체 길이
                useDays = today.day - checkDay +1
            else : # 오늘이 검칠일보다 작으면
                lastday = today - datetime.timedelta(days=today.day) # 전달의 마지막일이 전체 길이
                useDays = lastday.day + today.day - checkDay +1
            checkYear = lastday.year
            checkMonth = lastday.month
            monthDays = lastday.day
        self._ret['checkYear'] = checkYear
        self._ret['checkMonth'] = checkMonth
        self._ret['monthDays'] = monthDays
        self._ret['useDays'] = useDays
        if (checkDay >= 28): # 말일미면, 말일로 다시 셋팅
            self._ret['checkDay'] = checkDay
        _LOGGER.debug(f"## 검침시작 {checkYear}년 {checkMonth}월 {self._ret['checkDay']}일, 오늘 {today.month}월 {today.day}일, 검침일수:{monthDays}, 사용일수{useDays}, 남은일수{monthDays - useDays}")



    # 월별 동계, 하계 일수 구하기
    # checkDay = 시작일
    def calc_lengthUseDays(self) :
        checkDay = self._ret['checkDay']
        checkYear = self._ret['checkYear']
        checkMonth = self._ret['checkMonth']
        monthDays = self._ret['monthDays']
        etc = 0
        winter = 0
        summer = 0

        if checkMonth == 12 :
            nextYear = checkYear + 1
            nextMonth = 1
        else :
            nextYear = checkYear
            nextMonth = checkMonth + 1
        months = [
            ("mm1", checkYear, checkMonth , monthDays - checkDay +1),
            ("mm2", nextYear, nextMonth , checkDay -1)
        ]
        
        mmdiff = []
        # 전력량요금 계산에 사용
        for mm, year, month, monthleng in months:
            if month in [6,7,8] :
                summer += monthleng
                season = 'summer'
            elif month in [11,12,1,2] :
                winter += monthleng
                season = 'winter'
            else :
                etc += monthleng
                season = 'etc'
            yymm = ((year-2000)*100) + month
            self._ret[mm]['yymm'] = f'{yymm}'
            self._ret[mm]['season'] = season
            self._ret[mm]['useDays'] = monthleng

            priceYymm = self.price_find(f'{yymm}')
            mmdiff.append(season + priceYymm)

        # 시즌이 같고, 단가가 같으면 사용일을 하나로 합치기
        if mmdiff[0] == mmdiff[1] :
            self._ret['mm1']['useDays'] += self._ret['mm2']['useDays']
            self._ret['mm2']['useDays'] = 0

        _LOGGER.debug(f'검침월:{checkMonth} , 검침일:{checkDay}')
        _LOGGER.debug(f"시즌일수: 기타 {etc}, 동계 {winter}, 하계 {summer}, 현시즌:{season} ")


    # 요금제 설정
    def set_price(self):
        for mm in ['mm1','mm2'] :
            yymm = self._ret[mm]['yymm'] # 사용연월
            priceYymm = self.price_find(yymm)
            price = merge(CALC_PARAMETER, MONTHLY_PRICE[priceYymm])
            self._ret[mm]['price'] = price[self._ret['pressure']]


    # 기본요금(원미만 절사) : 30,800원
    # 20,864.52원 = 5kW x 6,160원 x 21일/31일
    # 9,935.48원 = 5kW x 6,160원 x 10일/31일
    def calc_basic(self):
        contractKWh = self._ret['contractKWh'] # 사용전력
        for mm in ['mm1','mm2'] :
            seasonDays = self._ret[mm]['useDays'] # 사용일수
            if (seasonDays == 0) :
                continue
            price = self._ret[mm]['price']
            self._ret[mm]['basicWon'] = math.floor(contractKWh * price['basic'] * seasonDays / self._ret['monthDays'] * 100) / 100
            _LOGGER.debug(f"기본요금 {self._ret[mm]['season']} {self._ret[mm]['basicWon']} = 계약사용량{contractKWh} * 기본요금{price['basic']} * 사용일수{seasonDays} / 월일수{self._ret['monthDays']}")
        self._ret['basicWon'] = math.floor(self._ret['mm1']['basicWon'] + self._ret['mm2']['basicWon'])
        _LOGGER.debug(f"기본요금 계 {self._ret['basicWon']} = {self._ret['mm1']['basicWon']} + {self._ret['mm2']['basicWon']}")


    # 역률요금(원미만 절사) : 1,416.8원
    # 959.77 = { 20,864.52 x ( 90 - 71 ) x 0.2% } + { 20,864.52 x ( 95 - 91 ) x 0.2% }
    # 457.03 = { 9,935.48 x ( 90 - 71 ) x 0.2% } + { 9,935.48 x ( 95 - 91 ) x 0.2% }
    def calc_factor(self):
        for mm in ['mm1','mm2'] :
            seasonDays = self._ret[mm]['useDays'] # 사용일수
            if (seasonDays == 0) :
                continue
            self._ret[mm]['factorWon'] = math.floor(((self._ret[mm]['basicWon'] * (90 - self._ret['lagging']) * 0.002) + (self._ret[mm]['basicWon'] * (95 - self._ret['leading']) * 0.002)) * 100) / 100
            _LOGGER.debug(f"역률요금 {self._ret[mm]['season']} {self._ret[mm]['factorWon']} = ( 기본요금{self._ret[mm]['basicWon']} * (90 - 지상역률{self._ret['lagging']}) * 0.002 ) + ((기본요금{self._ret[mm]['basicWon']} * (95 - 진상역율{self._ret['leading']}) * 0.002)) ")
        self._ret['factorWon'] = math.floor(self._ret['mm1']['factorWon'] + self._ret['mm2']['factorWon'])
        _LOGGER.debug(f"역률요금 계 {self._ret['factorWon']} = {self._ret['mm1']['factorWon']} + {self._ret['mm2']['factorWon']}")


    # 전력량요금(원미만 절사) : 9,264원
    # 7,180.8원 = 68kWh x 105.6원
    # 2,083.2원 = 32kWh x 65.1원
    def calc_usekwh(self):
        for mm in ['mm1','mm2'] :
            seasonDays = self._ret[mm]['useDays'] # 사용일수
            if (seasonDays == 0) :
                continue
            load = 0
            seasonN = {'summer':0,'etc':1,'winter':2}
            seasonNo = seasonN[self._ret[mm]['season']]
            seasonprice = self._ret[mm]['price']['section'][load][seasonNo]
            self._ret[mm]['usekwh'] = math.floor((self._ret['usekwh'] * seasonDays / self._ret['monthDays']) * 100) / 100
            self._ret[mm]['usekwhWon'] = math.floor(self._ret[mm]['usekwh'] * seasonprice * 100) / 100
            _LOGGER.debug(f"전력량요금 {load} {self._ret[mm]['season']} {self._ret[mm]['usekwhWon']} = ( 사용량{self._ret[mm]['usekwh']} * 사용일수{seasonDays} / 월일수{self._ret['monthDays']} ) * 단가{seasonprice} ")
        self._ret['usekwhWon'] = math.floor(self._ret['mm1']['usekwhWon'] + self._ret['mm2']['usekwhWon'])
        _LOGGER.debug(f"전력량요금 계 {self._ret['usekwhWon']} = {self._ret['mm1']['usekwhWon']} + {self._ret['mm2']['usekwhWon']}")


    # 기후환경요금(원미만 절사) : 730원
    # 496.4원 = 68kWh x 7.30원
    # 233.6원 = 32kWh x 7.30원
    #   * 전기요금 체계개편 적용일 전·후로 일수계산. 적용일 이후의 일수 반영

    # 연료비조정액(원미만 절사) : 500원
    # 340원 = 68kWh x 5.00원
    # 160원 = 32kWh x 5.00원
    #   * 연료비조정액은 일수계산 안 함

    # 전기요금 = 기본요금 + 전력량요금 + 기후환경요금 + 연료비조정요금 + 역률요금 + 200kWh이하감액 + 필수사용량보장공제액 + 복지할인금액 + 사용량0감액
    # 42,710원 = 30,800원 + 9,264원 + 730원 + 500원 + 1,416원 + 0원 + 0원 + 0원 + 0원

    # 부가가치세 = 전기요금 x 10% (원미만반올림)
    # 4,271원 = 42,710원 x 10%

    # 전력산업기반기금 = 전기요금 x 3.7% (10원미만 절사)
    # 1,580원 = 42,710원 x 3.7%

    # 청구금액(전기요금계 ＋ 부가가치세 ＋ 전력산업기반기금)
    # : 42,710원 ＋ 4,271원 ＋ 1,580원 ＝ 48,560원(10원미만 절사)




    def kwh2won(self, usekwh, today=None) :
        
        _LOGGER.debug(f'########### 전기사용량 : {usekwh}')
        usekwh = float(usekwh)
        if usekwh == 0 :
            self._ret['usekwh'] = 0.0001
        else :
            self._ret['usekwh'] = usekwh

        if today:
            self._ret['today'] = today

        _LOGGER.debug(f"오늘: {self._ret['today']}, 검침일: {self._ret['checkDay']}")
        
        self.calc_lengthDays()    # 월길이
        self.calc_lengthUseDays() # 동계, 하계, 기타 기간
        self.set_price() # 요금제 설정
        self.calc_basic() # 기본요금
        self.calc_factor() # 역률요금
        self.calc_usekwh() # 전력량요금
        # 기후환경요금
        # 연료비조정액
        # 합계
        # 부가세
        # 전력산업기금
        # 청구금액
        
        return self._ret



cfg = {
    'pressure' : 'F1-low',
    'checkDay' : 11, # 검침일
    'today' : datetime.datetime(2022,7,20, 22,42,0), # 오늘
    'contractKWh': 5, # 계약전력
    'lagging' : 81, # 지상역률 
    'leading' : 95, # 진상역률
    'welfareDcCfg' : 3, # 복지 요금할인 1: 유공자 장애인, 2: 사회복지시설, 3: 기초생활(생계.의료), 4: 기초생활(주거,복지), 5: 차상위계층
}

import pprint
K2W = kwh2won_api(cfg)
ret = K2W.kwh2won(100)
# K2W.calc_lengthDays()
# forc = K2W.energy_forecast(17)
# # pprint.pprint(ret)
