import math
import datetime
from dateutil.relativedelta import relativedelta
import logging
_LOGGER = logging.getLogger(__name__)

# # 로그의 출력 기준 설정
# _LOGGER.setLevel(logging.DEBUG)
# # log 출력 형식
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# # log 출력
# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)
# _LOGGER.addHandler(stream_handler)

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

# 단가표 정규식 치환
# 일반용 전력(갑) Ⅰ
# 찾을말
# ^([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# ^([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# ^([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# ^([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# ^([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# 바꿀말
# 'F1-low':     { 'section': [ [\1, \2, \3]] },
# 'F1-high-A1': { 'section': [ [\4, \5, \6]] },
# 'F1-high-A2': { 'section': [ [\7, \8, \9]] },
# 'F1-high-B1': { 'section': [ [\10, \11, \12]] },
# 'F1-high-B2': { 'section': [ [\13, \14, \15]] },
# 일반용 전력(갑) Ⅱ, 일반용 전력(을)
# 찾을말
# ^경부하\t([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# ^중간부하\t([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# ^최대부하\t([0-9\.]+)\t([0-9\.]+)\t([0-9\.]+)
# 바꿀말
# 'S-high-': { 'section': [ [\1, \2, \3], [\4, \5, \6], [\7, \8, \9] ] },

# 기본요금
MONTHLY_PRICE_BASIC = {
    '2101': {
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
    }
}

# 환경비용차감 + 기후환경요금 + 연료비조정액
MONTHLY_PRICE_ADJUSTMENT = {
    '2101': { 'adjustment' : [5, 5.3, -3] },
    '2109': { 'adjustment' : [5, 5.3, 0] },
    '2204': { 'adjustment' : [6.7, 7.3, 0] },
    '2207': { 'adjustment' : [6.7, 7.3, 5] },
    '2210': { 'adjustment' : [6.7, 7.3, 5] },
    '2301': { 'adjustment' : [8.8, 9, 5] }, # RPS 7.7 + ETS 1.1, 석탄발전 감축비용 0.2, 연료비 조정액 +5원
}

# 전력산업기금 요율
BASE_FUND = {
    '2101': { 'baseFundp': 0.037 },
    '2407': { 'baseFundp': 0.032 },
    '2507': { 'baseFundp': 0.027 },
}


MONTHLY_PRICE_SECTION = {
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
        'F1-low':     { 'section': [ [113, 72.5, 99.6]] },
        'F1-high-A1': { 'section': [ [123.2, 79.2, 110.9]] },
        'F1-high-A2': { 'section': [ [119.2, 74.9, 105.6]] },
        'F1-high-B1': { 'section': [ [121.1, 78.1, 107.9]] },
        'F1-high-B2': { 'section': [ [115.8, 72.8, 102.6]] },
        'F2-high-A1': { 'section': [ [70, 70, 78.7], [121.2, 77.4, 109.1], [143.7, 88.7, 123.9] ] },
        'F2-high-A2': { 'section': [ [64.7, 64.7, 73.4], [115.9, 72.1, 103.8], [138.4, 83.4, 118.6] ] },
        'F2-high-B1': { 'section': [ [69.4, 69.4, 78.4], [118, 75.3, 105.7], [134.4, 80.7, 119.9] ] },
        'F2-high-B2': { 'section': [ [64.1, 64.1, 73.1], [112.7, 70, 100.4], [129.1, 75.4, 114.6] ] },
        'S-high-A1': { 'section': [ [73.4, 73.4, 80.4], [126.3, 95.9, 126.5], [208.4, 126.6, 184] ] },
        'S-high-A2': { 'section': [ [67.9, 67.9, 74.9], [120.8, 90.4, 121], [202.9, 121.1, 178.5] ] },
        'S-high-A3': { 'section': [ [67, 67, 74.3], [120.2, 89.1, 120.4], [190.5, 112.8, 167.3] ] },
        'S-high-B1': { 'section': [ [76.5, 76.5, 83.5], [128.8, 98.8, 128.8], [210, 129.1, 185] ] },
        'S-high-B2': { 'section': [ [72.7, 72.7, 79.7], [125, 95, 125], [206.2, 125.3, 181.2] ] },
        'S-high-B3': { 'section': [ [71, 71, 78.1], [123.3, 93.4, 123.3], [204.6, 123.7, 179.5] ] },
        'S-high-C1': { 'section': [ [76, 76, 82.9], [128.9, 98.9, 128.5], [209.8, 129.3, 185.1] ] },
        'S-high-C2': { 'section': [ [71.3, 71.3, 78.2], [124.2, 94.2, 123.8], [205.1, 124.6, 180.4] ] },
        'S-high-C3': { 'section': [ [70.2, 70.2, 77.1], [123.1, 93.1, 122.7], [204, 123.5, 179.3] ] }
    },
    '2301': {
        'F1-low':     { 'section': [ [124.4, 83.9, 111]] },
        'F1-high-A1': { 'section': [ [134.6, 90.6, 122.3]] },
        'F1-high-A2': { 'section': [ [130.6, 86.3, 117]] },
        'F1-high-B1': { 'section': [ [132.5, 89.5, 119.3]] },
        'F1-high-B2': { 'section': [ [127.2, 84.2, 114]] },
        'F2-high-A1': { 'section': [ [81.4, 81.4, 90.1], [132.6, 88.8, 120.5], [155.1, 100.1, 135.3] ] },
        'F2-high-A2': { 'section': [ [76.1, 76.1, 84.8], [127.3, 83.5, 115.2], [149.8, 94.8, 130] ] },
        'F2-high-A3': { 'section': [ [80.8, 80.8, 89.8], [129.4, 86.7, 117.1], [145.8, 92.1, 131.3] ] },
        'F2-high-A4': { 'section': [ [75.5, 75.5, 84.5], [124.1, 81.4, 111.8], [140.5, 86.8, 126] ] },
        'S-high-A1': { 'section': [ [84.8, 84.8, 91.8], [137.7, 107.3, 137.9], [219.8, 138, 195.4] ] },
        'S-high-A2': { 'section': [ [79.3, 79.3, 86.3], [132.2, 101.8, 132.4], [214.3, 132.5, 189.9] ] },
        'S-high-A3': { 'section': [ [78.4, 78.4, 85.7], [131.6, 100.5, 131.8], [201.9, 124.2, 178.7] ] },
        'S-high-B1': { 'section': [ [87.9, 87.9, 94.9], [140.2, 110.2, 140.2], [221.4, 140.5, 196.4] ] },
        'S-high-B2': { 'section': [ [84.1, 84.1, 91.1], [136.4, 106.4, 136.4], [217.6, 136.7, 192.6] ] },
        'S-high-B3': { 'section': [ [82.4, 82.4, 89.5], [134.7, 104.8, 134.7], [216, 135.1, 190.9] ] },
        'S-high-C1': { 'section': [ [87.4, 87.4, 94.3], [140.3, 110.3, 139.9], [221.2, 140.7, 196.5] ] },
        'S-high-C2': { 'section': [ [82.7, 82.7, 89.6], [135.6, 105.6, 135.2], [216.5, 136, 191.8] ] },
        'S-high-C3': { 'section': [ [81.6, 81.6, 88.5], [134.5, 104.5, 134.1], [215.4, 134.9, 190.7] ] },
    },
    '2305': {
        'F1-low':     { 'section': [ [132.4, 91.9, 119]] },
        'F1-high-A1': { 'section': [ [142.6, 98.6, 130.3]] },
        'F1-high-A2': { 'section': [ [138.6, 94.3, 125]] },
        'F1-high-B1': { 'section': [ [140.5, 97.5, 127.3]] },
        'F1-high-B2': { 'section': [ [135.2, 92.2, 122]] },
        'F2-high-A1': { 'section': [ [89.4, 89.4, 98.1], [140.6, 96.8, 128.5], [163.1, 108.1, 143.3] ] },
        'F2-high-A2': { 'section': [ [84.1, 84.1, 92.8], [135.3, 91.5, 123.2], [157.8, 102.8, 138] ] },
        'F2-high-A3': { 'section': [ [88.8, 88.8, 97.8], [137.4, 94.7, 125.1], [153.8, 100.1, 139.3] ] },
        'F2-high-A4': { 'section': [ [83.5, 83.5, 92.5], [132.1, 89.4, 119.8], [148.5, 94.8, 134] ] },
        'S-high-A1': { 'section': [ [92.8, 92.8, 99.8], [145.7, 115.3, 145.9], [227.8, 146, 203.4] ] },
        'S-high-A2': { 'section': [ [87.3, 87.3, 94.3], [140.2, 109.8, 140.4], [222.3, 140.5, 197.9] ] },
        'S-high-A3': { 'section': [ [86.4, 86.4, 93.7], [139.6, 108.5, 139.8], [209.9, 132.2, 186.7] ] },
        'S-high-B1': { 'section': [ [95.9, 95.9, 102.9], [148.2, 118.2, 148.2], [229.4, 148.5, 204.4] ] },
        'S-high-B2': { 'section': [ [92.1, 92.1, 99.1], [144.4, 114.4, 144.4], [225.6, 144.7, 200.6] ] },
        'S-high-B3': { 'section': [ [90.4, 90.4, 97.5], [142.7, 112.8, 142.7], [224, 143.1, 198.9] ] },
        'S-high-C1': { 'section': [ [95.4, 95.4, 102.3], [148.3, 118.3, 147.9], [229.2, 148.7, 204.5] ] },
        'S-high-C2': { 'section': [ [90.7, 90.7, 97.6], [143.6, 113.6, 143.2], [246.5, 144, 199.8] ] },
        'S-high-C3': { 'section': [ [89.6, 89.6, 96.5], [142.5, 112.5, 142.1], [223.4, 142.9, 198.7] ] },
    }
}

class kwh2won_api:
    def __init__(self, cfg):
        ret = {
            'welfareDc' : 0, # 복지할인요금
            'contractKWh' : 0, # 계약전력 contractKWh
            'reactive' : 0, # 무효천력량계 Reactive Power meter
            'lagging' : 90, # 지상역률 Lagging Power Factor
            'leading' : 95, # 진상역률 Leading
            'pressure' : 'F1-low', # 용도, 수전전압
            'usekwh': 0,     # 사용량
            'minkwh': 0, # 심야 (경) 사용량
            'medkwh': 0, # 주간 (중간) 사용량
            'maxkwh': 0, # 저녁 (최대) 사용량

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
                'minkwh': 0, # 심야 (경) 사용량
                'medkwh': 0, # 주간 (중간) 사용량
                'maxkwh': 0, # 저녁 (최대) 사용량
                'basicWon': 0,   # 기본요금
                'factorWon': 0,   # 역률요금
                'usekwhWon': 0,     # 전력량요금
                'elecBasicDc': 0, # 필수사용량보장공제
                'diffWon': 0,    # 환경비용차감
                'climateWon': 0, # 기후환경요금
                'fuelWon': 0,    # 연료비조정액
                'useDays': 0,    # 사용일수
                'welfareDcWon': 0,  # 복지할인
                'price': {} # 단가
            },
            'mm2' : {
                'yymm': '',     # 사용년월
                'season': 0, # 시즌
                'usekwh': 0,     # 사용량
                'minkwh': 0, # 심야 (경) 사용량
                'medkwh': 0, # 주간 (중간) 사용량
                'maxkwh': 0, # 저녁 (최대) 사용량
                'basicWon': 0,   # 기본요금
                'factorWon': 0,   # 역률요금
                'usekwhWon': 0,     # 전력량요금
                'elecBasicDc': 0, # 필수사용량보장공제
                'diffWon': 0,    # 환경비용차감
                'climateWon': 0, # 기후환경요금
                'fuelWon': 0,    # 연료비조정액
                'useDays': 0,    # 사용일수
                'welfareDcWon': 0,  # 복지할인
                'price': {} # 단가
            },
            'basicWon': 0,   # 기본요금
            'usekwhWon': 0,     # 전력량요금
            'diffWon': 0, # 환경비용차감
            'climateWon': 0, # 기후환경요금
            'fuelWon': 0, # 연료비조정액
            'factorWon': 0, # 역률요금
            'elecBasicDc': 0, # 필수사용량보장공제
            'elecBasic200Dc': 0, # 200kWh이하 감액
            'welfareDcWon': 0, # 복지 요금할인
            'zeorDcWon': 0, # 사용량0감액
            'elecSumWon': 0, # 전기요금계
            'vat': 0, # 부가가치세
            'baseFund': 0, # 전력산업기반기금
            'total': 0, # 청구금액
        }
        ret.update(cfg)
        self._ret = ret



    # 당월 단가 찾기
    def price_find(self, prices, yymm):
        cnt = -1
        listym = list(prices.keys())
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

        forcest = round(energy / ((((useDays - 1) * 24) + today.hour) * 60 + today.minute + 1) * (monthDays * 24 * 60), 1)
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
            yymm = f'{yymm}'
            self._ret[mm]['yymm'] = yymm
            self._ret[mm]['season'] = season
            self._ret[mm]['useDays'] = monthleng

            basicYymm = self.price_find(MONTHLY_PRICE_BASIC, yymm)
            adjustYymm = self.price_find(MONTHLY_PRICE_ADJUSTMENT, yymm)
            priceYymm = self.price_find(MONTHLY_PRICE_SECTION, yymm)
            _LOGGER.debug(f'{mm} : season{season} + basic{basicYymm} + adjust{adjustYymm} + section{priceYymm}')
            mmdiff.append(season + basicYymm + adjustYymm + priceYymm)
            
        # 연료비조정액 빼고 단가 바교해서 같으면 합치는 것으로 수정 해야 함.
        # 시즌이 같고, 단가가 같으면 사용일을 하나로 합치기
        if mmdiff[0] == mmdiff[1] :
            self._ret['mm1']['useDays'] += self._ret['mm2']['useDays']
            self._ret['mm2']['useDays'] = 0

        _LOGGER.debug(f'검침월:{checkMonth} , 검침일:{checkDay}')
        _LOGGER.debug(f"시즌일수: 기타 {etc}, 동계 {winter}, 하계 {summer}, 현시즌:{season} ")


    # 단가 설정
    def set_price(self):
        for mm in ['mm1','mm2'] :
            yymm = self._ret[mm]['yymm'] # 사용연월
            pressure = self._ret['pressure'] # 용도, 수전전압
            basicYymm = self.price_find(MONTHLY_PRICE_BASIC, yymm) # 기본요금
            adjustYymm = self.price_find(MONTHLY_PRICE_ADJUSTMENT, yymm) # 화경비용, 기후환경, 연료비조정
            priceYymm = self.price_find(MONTHLY_PRICE_SECTION, yymm) # 용도, 시즌 시간 별 단가
            basefundYymm = self.price_find(BASE_FUND, yymm) # 용도, 시즌 시간 별 단가
            price = merge(MONTHLY_PRICE_BASIC[basicYymm][pressure], MONTHLY_PRICE_ADJUSTMENT[adjustYymm])
            price = merge(price, MONTHLY_PRICE_SECTION[priceYymm][pressure])
            self._ret[mm]['price'] = merge(price, BASE_FUND[basefundYymm])


    # 계약전력 5kW, 월간 100kWh 사용시 전기요금 계산, 역률(지상:71%, 진상:91%) 2022/08/11~2022/09/10

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
            self._ret[mm]['basicWon'] = round(contractKWh * price['basic'] * seasonDays / self._ret['monthDays'], 2)
            _LOGGER.debug(f"기본요금 {self._ret[mm]['season']} {self._ret[mm]['basicWon']} = 계약사용량{contractKWh} * 기본요금{price['basic']} * 사용일수{seasonDays} / 월일수{self._ret['monthDays']}")
        self._ret['basicWon'] = math.floor(self._ret['mm1']['basicWon'] + self._ret['mm2']['basicWon'])
        _LOGGER.debug(f"기본요금 계 {self._ret['basicWon']} = {self._ret['mm1']['basicWon']} + {self._ret['mm2']['basicWon']}")


    # 역률요금(원미만 절사) : 1,416.8원
    # 959.77 = { 20,864.52 x ( 90 - 71 ) x 0.2% } + { 20,864.52 x ( 95 - 91 ) x 0.2% }
    # 457.03 = { 9,935.48 x ( 90 - 71 ) x 0.2% } + { 9,935.48 x ( 95 - 91 ) x 0.2% }
    def calc_factor(self):
        for mm in ['mm1','mm2'] :
            seasonDays = self._ret[mm]['useDays'] # 사용일수
            if (seasonDays == 0 or self._ret[mm]['usekwh'] == 0) :
                continue
            self._ret[mm]['factorWon'] = round(((self._ret[mm]['basicWon'] * (90 - self._ret['lagging']) * 0.002) + (self._ret[mm]['basicWon'] * (95 - self._ret['leading']) * 0.002)) * 100) / 100
            _LOGGER.debug(f"역률요금 {self._ret[mm]['season']} {self._ret[mm]['factorWon']} = ( 기본요금{self._ret[mm]['basicWon']} * (90 - 지상역률{self._ret['lagging']}) * 0.002 ) + ((기본요금{self._ret[mm]['basicWon']} * (95 - 진상역율{self._ret['leading']}) * 0.002)) ")
        self._ret['factorWon'] = math.floor(self._ret['mm1']['factorWon'] + self._ret['mm2']['factorWon'])
        _LOGGER.debug(f"역률요금 계 {self._ret['factorWon']} = {self._ret['mm1']['factorWon']} + {self._ret['mm2']['factorWon']}")


    # 전력량요금(원미만 절사) : 9,264원 (일반용 갑 1)
    # 7,180.8원 = 68kWh x 105.6원
    # 2,083.2원 = 32kWh x 65.1원
    def calc_usekwh1(self):
        load = 0
        for mm in ['mm1','mm2'] :
            seasonDays = self._ret[mm]['useDays'] # 사용일수
            if (seasonDays == 0) :
                continue
            seasonN = {'summer':0,'etc':1,'winter':2}
            seasonNo = seasonN[self._ret[mm]['season']]
            seasonprice = self._ret[mm]['price']['section'][load][seasonNo]
            self._ret[mm]['usekwh'] = round(self._ret['usekwh'] * seasonDays / self._ret['monthDays'])
            self._ret[mm]['usekwhWon'] = round(self._ret[mm]['usekwh'] * seasonprice, 2)
            _LOGGER.debug(f"전력량요금 {self._ret[mm]['season']} {self._ret[mm]['usekwhWon']} = 사용량{self._ret[mm]['usekwh']} * 단가{seasonprice} ")
        self._ret['usekwhWon'] = math.floor(self._ret['mm1']['usekwhWon'] + self._ret['mm2']['usekwhWon'])
        _LOGGER.debug(f"전력량요금 계 {self._ret['usekwhWon']} = {self._ret['mm1']['usekwhWon']} + {self._ret['mm2']['usekwhWon']}")


    # 전력량요금(원미만 절사) : 9,780원
    # 7,471.6원 = 876.4원 + 3,869.2원 + 2,726원

    # 경부하요금 : 876.4원 = 14kWh x 62.6원
    # 중간부하요금 : 3,869.2원 = 34kWh x 113.8원
    # 최대부하요금 : 2,726원 = 20kWh x 136.3원2,308.6원 = 375.6원 + 1,120원 + 813원

    # 경부하요금 : 375.6원 = 6kWh x 62.6원
    # 중간부하요금 : 1,120원 = 16kWh x 70원
    # 최대부하요금 : 813원 = 10kWh x 81.3원
    def calc_usekwh2(self):
        seasonN = {'summer':0,'etc':1,'winter':2}
        loadN = {'minkwh':0,'medkwh':1,'maxkwh':2}
        for mm in ['mm1','mm2'] :
            seasonDays = self._ret[mm]['useDays'] # 사용일수
            if (seasonDays == 0) :
                continue
            seasonNo = seasonN[self._ret[mm]['season']]
            self._ret[mm]['usekwh'] = round(self._ret['usekwh'] * seasonDays / self._ret['monthDays'])
            for load in ['minkwh','medkwh','maxkwh']:
                seasonprice = self._ret[mm]['price']['section'][loadN[load]][seasonNo]
                self._ret[mm][load] = round(self._ret[load] * seasonDays / self._ret['monthDays'])
                self._ret[mm][load+'Won'] = round(self._ret[mm][load] * seasonprice, 4)
                _LOGGER.debug(f"전력량요금 {self._ret[mm]['season']} {load} {self._ret[mm][load+'Won']} = 사용량{self._ret[mm][load]} * 단가{seasonprice} ")
            self._ret[mm]['usekwhWon'] = round(self._ret[mm]['minkwhWon'] + self._ret[mm]['medkwhWon'] + self._ret[mm]['maxkwhWon'])
            _LOGGER.debug(f"전력량요금 {self._ret[mm]['season']} 계 {self._ret[mm]['usekwhWon']} = minkwhWon{self._ret[mm]['minkwhWon']} + medkwhWon{self._ret[mm]['medkwhWon']} + maxkwhWon{self._ret[mm]['maxkwhWon']} ")
        self._ret['usekwhWon'] = math.floor(self._ret['mm1']['usekwhWon'] + self._ret['mm2']['usekwhWon'])
        _LOGGER.debug(f"전력량요금 계 {self._ret['usekwhWon']} = {self._ret['mm1']['usekwhWon']} + {self._ret['mm2']['usekwhWon']}")


    # 기후환경요금(원미만 절사) : 730원
    # 496.4원 = 68kWh x 7.30원
    # 233.6원 = 32kWh x 7.30원
    #   * 전기요금 체계개편 적용일 전·후로 일수계산. 적용일 이후의 일수 반영
    def calc_climate(self):
        for mm in ['mm1','mm2'] :
            seasonDays = self._ret[mm]['useDays'] # 사용일수
            if (seasonDays == 0) :
                continue
            adjustment1 = self._ret[mm]['price']['adjustment'][1]
            self._ret[mm]['climateWon'] = round(self._ret[mm]['usekwh'] * adjustment1, 2)
            _LOGGER.debug(f"기후환경요금 {self._ret[mm]['season']} {self._ret[mm]['climateWon']} = 사용량{self._ret[mm]['usekwh']} * 단가{adjustment1} ")
        self._ret['climateWon'] = math.floor(self._ret['mm1']['climateWon'] + self._ret['mm2']['climateWon'])
        _LOGGER.debug(f"기후환경요금 계 {self._ret['climateWon']} = {self._ret['mm1']['climateWon']} + {self._ret['mm2']['climateWon']}")


    # 연료비조정액(원미만 절사) : 500원
    # 340원 = 68kWh x 5.00원
    # 160원 = 32kWh x 5.00원
    #   * 연료비조정액은 일수계산 안 함
    # 요금 산정기준은 검침일인데 6월1일부터6월30일 까지 사용한것을 7월1일 검침하는 것 
    def calc_fuel(self):
        # 검침 시작일의 한달 후를 구함.
        d = datetime.date(self._ret['checkYear'], self._ret['checkMonth'], self._ret['checkDay'])
        d = d + relativedelta(months=1)
        yymm = d.strftime("%y%m")
        adjustYymm = self.price_find(MONTHLY_PRICE_ADJUSTMENT,yymm)
        adjustment2 = MONTHLY_PRICE_ADJUSTMENT[adjustYymm]['adjustment'][2]
        self._ret['fuelWon'] = math.floor(self._ret['usekwh'] * adjustment2)
        _LOGGER.debug(f"연료비조정액 {self._ret['fuelWon']} = 사용량{self._ret['usekwh']} * 단가{adjustment2} ")



    # 전기요금 = 기본요금 + 전력량요금 + 기후환경요금 + 연료비조정요금 + 역률요금 + 200kWh이하감액 + 필수사용량보장공제액 + 복지할인금액 + 사용량0감액
    # 42,710원 = 30,800원 + 9,264원 + 730원 + 500원 + 1,416원 + 0원 + 0원 + 0원 + 0원
    def calc_elec(self):
        basicWon = self._ret['basicWon'] # 기본요금
        usekwhWon = self._ret['usekwhWon'] # 전력량요금
        climateWon = self._ret['climateWon'] # 기후환경요금
        fuelWon = self._ret['fuelWon'] # 연료비조정요금
        factorWon = self._ret['factorWon'] # 역률요금
        # elecBasic200Dc = self._ret['elecBasic200Dc'] # 200kWh이하감액
        # elecBasicDc = self._ret['elecBasicDc'] # 필수사용량보장공제액
        welfareDcWon = self._ret['welfareDcWon'] # 복지할인금액
        zeorDcWon = 0  # 사용량0감액
        # 사용량0감액
        if (self._ret['usekwh'] == 0):
            zeorDcWon = basicWon / -2
            _LOGGER.debug(f"사용량0감액{zeorDcWon} = 기본요금{basicWon} / -50%")
        self._ret['zeorDcWon'] = zeorDcWon # 사용량0감액
        elecSumWon = basicWon + usekwhWon + climateWon + fuelWon + factorWon + welfareDcWon + zeorDcWon # 전기요금
        self._ret['elecSumWon'] = elecSumWon # 전기요금
        _LOGGER.debug(f"전기요금{elecSumWon} = 기본요금{basicWon} + 전력량요금{usekwhWon} + 기후환경요금{climateWon} + 연료비조정요금{fuelWon} + 역률요금{factorWon} + 복지할인금액{welfareDcWon} + 사용량0감액{zeorDcWon}")


    # 복지할인(원미만 절사) : -12,812원
    # ·사회복지시설 할인 : -12,812원
    # 할인액 : -8,951.7원 = (29,839원 / 1) x 30% x -1
    # 할인액 : -3,860.4원 = (12,868원 / 1) x 30% x -1
    def welfareDc(self):
        if (self._ret['welfareDc'] > 0):
            for mm in ['mm1','mm2'] :
                seasonDays = self._ret[mm]['useDays'] # 사용일수
                if (seasonDays == 0) :
                    continue
                welfareDcWon = round(self._ret['elecSumWon'] * seasonDays / self._ret['monthDays'] * -0.3, 2)
                self._ret[mm]['welfareDcWon'] = welfareDcWon
                _LOGGER.debug(f"사회복지시설 할인 {self._ret[mm]['season']} {self._ret[mm]['welfareDcWon']} = 사용량{round(self._ret['elecSumWon'] * seasonDays / self._ret['monthDays'], 2)}({self._ret['elecSumWon']} * {seasonDays} / {self._ret['monthDays']}) x -30% ")
            self._ret['welfareDcWon'] = math.floor(self._ret['mm1']['welfareDcWon'] + self._ret['mm2']['welfareDcWon'])
            _LOGGER.debug(f"사회복지시설 할인 계 {self._ret['welfareDcWon']} = {self._ret['mm1']['welfareDcWon']} + {self._ret['mm2']['welfareDcWon']}")



    # 전력산업기반기금(10원미만 절사)
    def base_fund(self,elecSumWon):
        baseFund = 0
        for mm in ['mm1','mm2']:
            baseFundp = self._ret[mm]['price']['baseFundp']
            baseFund = math.floor(elecSumWon * baseFundp * self._ret[mm]['useDays'] / self._ret['monthDays'])
            self._ret[mm]['baseFund'] = baseFund
            _LOGGER.debug(f"전력산업기반기금({self._ret[mm]['yymm']}):{baseFund}원 = 전기요금계{elecSumWon} * {baseFundp} * {self._ret[mm]['useDays']} / {self._ret['monthDays']}")
        self._ret['baseFund'] = math.floor((self._ret['mm1']['baseFund'] + self._ret['mm2']['baseFund']) /10)*10
        _LOGGER.debug(f"전력산업기반기금(10원미만 절사):{self._ret['baseFund']}원 = {self._ret['mm1']['baseFund']} + {self._ret['mm2']['baseFund']}")
        return self._ret['baseFund']


    # 부가가치세 = 전기요금 x 10% (원미만반올림)
    # 4,271원 = 42,710원 x 10%

    # 전력산업기반기금 = 전기요금 x 3.7% (10원미만 절사)
    # 1,580원 = 42,710원 x 3.7%

    # 청구금액(전기요금계 ＋ 부가가치세 ＋ 전력산업기반기금)
    # : 42,710원 ＋ 4,271원 ＋ 1,580원 ＝ 48,560원(10원미만 절사)
    def calc_total(self):
        # 부가가치세 = 전기요금 x 10% (원미만반올림)
        elecSumWon = self._ret['elecSumWon']
        vat = round(elecSumWon * 0.1)
        self._ret['vat'] = vat
        _LOGGER.debug(f"부가가치세{vat} = 전기요금{elecSumWon} x 10% ")


        # 전력산업기반기금 = 전기요금 x 3.7% (10원미만 절사)
        baseFund = self.base_fund(elecSumWon)

        # 청구금액 (전기요금계 ＋ 부가가치세 ＋ 전력산업기반기금)
        total = math.floor((elecSumWon + vat + baseFund) / 10 ) * 10
        self._ret['total'] = total
        _LOGGER.debug(f"청구금액{total} = 전기요금{elecSumWon} + 부가가치세{vat} + 전력산업기반기금{baseFund} ")



    def kwh2won(self, usekwh={'usekwh':0, 'minkwh':0, 'medkwh':0, 'maxkwh':0, 'lagging':90, 'leading':95}, today=None) :
        
        pressure = self._ret['pressure'].split('-')
        if pressure[0] == 'F1': 
            usekwh1 = float(usekwh['usekwh'])
            self._ret['usekwh'] = usekwh1
            _LOGGER.debug(f"########### 전기사용량 : usekwh{usekwh1}, lagging{usekwh['lagging']}, leading{usekwh['leading']}")
        else:
            minkwh = float(usekwh['minkwh'])
            medkwh = float(usekwh['medkwh'])
            maxkwh = float(usekwh['maxkwh'])
            usekwh1 =  minkwh + medkwh + maxkwh
            self._ret['usekwh'] = usekwh1
            self._ret['minkwh'] = minkwh
            self._ret['medkwh'] = medkwh
            self._ret['maxkwh'] = maxkwh
            _LOGGER.debug(f"########### 전기사용량 : usekwh{usekwh1}, lagging{usekwh['lagging']}, leading{usekwh['leading']}, minkwh{minkwh}, medkwh{medkwh}, maxkwh{maxkwh}")

        self._ret['lagging'] = usekwh['lagging']
        self._ret['leading'] = usekwh['leading']
        if today:
            self._ret['today'] = today

        _LOGGER.debug(f"오늘: {self._ret['today']}, 검침일: {self._ret['checkDay']}")
        
        self.calc_lengthDays()    # 월길이
        self.calc_lengthUseDays() # 동계, 하계, 기타 기간
        self.set_price() # 요금제 설정
        self.calc_basic() # 기본요금
        self.calc_factor() # 역률요금
        pressure = self._ret['pressure'].split('-')
        if pressure[0] == 'F1': 
            self.calc_usekwh1() # 전력량요금 - 갑1
        else:
            self.calc_usekwh2() # 전력량요금 - 갑2,을
        self.calc_climate() # 기후환경요금
        self.calc_fuel() # 연료비조정액
        self.calc_elec() # 전기요금
        if (self._ret['welfareDc'] > 0):
            self.welfareDc() # 사회복지할인
            self.calc_elec() # 전기요금
        self.calc_total() # 청구금액
        
        return self._ret



# cfg = {
#     'pressure': 'F2-high-A1',
#     'checkDay': 11, # 검침일
#     'today': datetime.datetime(2024,6,20, 22,42,0), # 오늘
#     'contractKWh': 5, # 계약전력
#     'lagging': 71, # 지상역률 
#     'leading': 91, # 진상역률
#     'welfareDcCfg': 0, # 복지 요금할인 1: 사회복지시설
# }
# usekwh = {
#     'usekwh':0,
#     'minkwh':0,
#     'medkwh':0,
#     'maxkwh':0,
#     'lagging':90,
#     'leading':95
# }
# import pprint
# K2W = kwh2won_api(cfg)
# ret = K2W.kwh2won(usekwh) # 
# # K2W.calc_lengthDays()
# # forc = K2W.energy_forecast(17)
# # pprint.pprint(ret)
