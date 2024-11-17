# 전기요금계산 센서 (일반용) for HomeAssistant

## 주요기능
- 일반용 전기요금 계산 센서
  - 전기 사용량을 사용요금으로 계산
  - 갑1 저압, 고압 지원
- 예상사용량 센서
- 예상사용요금 센서

<br>

## 한전 전기요금 자료 링크
- [한전 전기요금계산기](https://cyber.kepco.co.kr/ckepco/front/jsp/CY/J/A/CYJAPP000NFL.jsp)
- [전기요금표 일반용](https://cyber.kepco.co.kr/ckepco/front/jsp/CY/E/E/CYEEHP00102.jsp)
<br>

## 스크린샷
![kwh2wonGeneral](https://user-images.githubusercontent.com/41262994/189909716-830c056a-5878-475a-90bd-7831afa517f3.png)

<br>

## 설치
- 수동설치 또는 HACS를 이용해 설치를 할수 있습니다.
### 수동
- HA 설치 경로 아래 custom_components에 kwh_to_won_general폴더 안의 전체 파일을 복사해줍니다.<br>
  `<config directory>/custom_components/kwh_to_won_general/`<br>
- Home-Assistant 를 재시작합니다<br>
### HACS
- HACS > Integretions > 우측상단 메뉴 > Custom repositories 선택
- `https://github.com/dugurs/kwh_to_won_general` 주소 입력, Category에 'integration' 선택 후, 저장
- HACS > Integretions 메뉴 선택 후, `kwh_to_won_general` 혹은 `전기요금 계산 센서` 검색하여 설치

<br>


## 통합구성요소 추가
- 구성 > 통합구성요소 > 통합구성요소 추가하기 > 전기요금 계산 (일반용 갑1) 센서 > 필수요소를 모두 입력후, 확인.

### 입력 사항 (필수)
- 생성할 기기의 이름을 입력하세요
- 검침일을 입력하세요 (시작일)
- 사용용도를 선택하세요
- 계약전력을 입력하세요
- 복지할인 해당사항을 선택하세요
- 월간 전기 사용량 센서를 입력하세요
### 입력 사항 (옵션)
- 지상역률센서 혹은 값를 입력하세요(기본값90)
- 진상역률센서 혹은 값를 입력하세요(기본값95)
- 전월 월간 전기 사용량 센서를 입력하세요
- 전월 지상역률센서 혹은 값를 입력하세요
- 전월 진상역률센서 혹은 값를 입력하세요
- 사용량 보정계수. 0이면 사용안함. (실제사용량 / 측정사용량 = 보정계수)
### 월간 누적 사용량 센서 및 전월 사용량 센서
- 검침일에 맞줘 카운팅되는 월간 누적 사용량 센서가 있어야 합니다.
- 없다면 아래와같이 [`utility_meter`](https://www.home-assistant.io/integrations/utility_meter/)를 이용해 만들어줘야 합니다.

```

# 매달 11일 0시 0분에 리셋 (검침 시작일 11일)
utility_meter:
  example_energy_monthly:
    source: sensor.example_energy
    cycle: monthly
    offset:
      days: 10
      
```
<br>

- 전월 사용량 센서는 다음과 같이 만들수 있습니다. [`template`](https://www.home-assistant.io/integrations/template/) 


```
template:
  - sensor:
      - name: "example_energy_prev_monthly"
        unique_id: example_energy_prev_monthly
        unit_of_measurement: kWh
        state: "{{ state_attr('sensor.example_energy_monthly','last_period') |round(1) }}"
        device_class: energy
        attributes:
          state_class: measurement
```
### 생성되는 센서
- 통합구성요소 추가시 이름을 `test`로 했다면 다음과 같은 3개의 센서가 생성됩니다.
  - `sensor.test_kwhto_won` 전기요금 센서
  - `sensor.test_kwhto_forecast` 예상 사용량 센서
  - `sensor.test_kwhto_forecast_won` 예상 전기요금 센서
- 전월 사용량 센서를 선택 했다면 다름과 같은 1개의 센서가 추가로 생성 됩니다.
  - `sensor.test_kwhto_won_prev` 전월 전기요금 센서
- 보정계수를 0보다 크게 설정하면 다름과 같은 1개의 센서가 추가로 생성 됩니다.
  - `sensor.test_kwhto_kwh` 전기사용량 센서
  - 보정계수 = 실제(검침)사용량 / 측정(센서)사용량

<br>

## 보완 예정 사항
- 
<br>

## 발견된 문제점
- 전월 전기요금 센서 생성 후 사용안한으로 변경시 자동제거 안됨(수동삭제 가능)
<br>


<br>

## 판올림
| Version | Date        | 내용              |
| :-----: | :---------: | ----------------------- |
| v0.0.1  | 2022.09.13  | 일반용 갑1 저압 및 고압 지원 |
| v0.0.2  | 2022.09.14  | 역률 고정값으로 입력 가능하게 |
| v0.0.3  | 2022.09.14  | 역률값 미입력시 type error 수정 |
| v0.0.4  | 2022.09.15  | debug 로그 출력 제거 |
| v0.0.5  | 2022.10.01  | 22년 10월 단가 인상분 반영 |
| v0.0.6  | 2023.01.01  | 23년 1월 단가 인상분 반영 |
| v0.0.7  | 2023.01.07  | 비화성화된 엔터티 업데이트 오류 해결 [@n-andflash](https://github.com/dugurs/kwh_to_won/issues/4) |
| v0.0.8  | 2023.02.21  | 월간센서 선택 방법 entity selector로 수정 |
| v0.0.9  | 2023.05.04 | HA 2023.5이상 오류 수정 |
| v0.0.10 | 2023.05.16 | 단가인상 적용(8원) 5월16일부터 적용 이라 5월분은 오차발생(월단위 계산방식), 취약계층 할인 미반영 |
| v0.0.11 | 2024.01.05 | HA Core 2025.01 대응  |
| v0.0.12 | 2024.03.05 | HA Core 2025.01 대응  |
| v0.0.14 | 2024.08.20 | 전력산업기반기금 인하 적용  |
| v0.0.15 | 2024.11.17 | HA Core 2025.05 대응  |

