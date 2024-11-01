## 게임 제목: Soul Knight

+ 간단 소개: "Soul Knight"을 모작한 게임입니다. 캐릭터와 함께 던전을 탐험하며 적들과 싸우는 액션 RPG입니다.
랜덤 생성된 던전과 흥미로운 아이템을 통해 플레이어는 매번 새로운 경험을 하게 됩니다.

+ 핵심 메카닉:
  + 랜덤 생성 던전: 매번 다른 레벨과 적들.
  + 캐릭터 능력: 캐릭터의 고유한 스킬.
  + 무기 조합: 다양한 무기를 조합하여 전투 전략을 세울 수 있음.

+ 예상 게임 실행 흐름
  + 적과의 전투
  
  ![gameplay](https://github.com/user-attachments/assets/60651abb-191f-43cd-a80d-b7b3b1d6a31f)

  + 현재까지의 진행상황과 앞으로 갈 수 있는 위치를 보여주는 맵
  
  ![gameplay2](https://github.com/user-attachments/assets/135857a1-81c5-485b-83f8-822699400e2c)

  + 보스와의 전투
  
  ![boss](https://github.com/user-attachments/assets/ef60b486-2f95-4744-92ee-47afa6e5b2f5)


+ 개발 내용
  + Scene 종류 및 구성
    + 메인 메뉴: 시작, 옵션, 종료 버튼.
    + 던전: 랜덤 생성된 던전, 적과의 전투
    + 게임 종료 화면: 결과 확인.


  + GameObject 종류 및 구성
    + 캐릭터: 플레이어 캐릭터, 캐릭터의 고유 능력.
    + 무기 : 다양 공격 방식이 있는 무기
    + 적: 다양한 종류의 몬스터.
    + 보스: 최종 보스.
    + 아이템: 무기, 회복 아이템.
    + 환경 요소: 벽, 장애물.


+ 각 클래스의 역할
  + Player: 플레이어 캐릭터의 속성과 행동 정의.
    + 구르기 기능
      + 캐릭터가 구르면 무적 상태가 되고, 일정 시간동안 회피할 수 있습니다.
      + 구르는 동안 적의 공격을 받지 않으며, 구르기가 끝난 후 잠시 동안 공격 속도가 증가합니다.
    + 무기 장착
      + 속성 : current_weapon() (현재 장착된 무기)
      + 설명 : 특정 무기를 장착하고, 2개까지 무기를 가지고 다닐 수 있다.
    + 메서드: draw(), update(), attack(), move()

  + Weapon: 무기의 속성과 효과 정의.
    + 속성: name, damage, range, type (근접/원거리)
    + 설명: 무기의 공격 방식을 정의하며, 공격 시 플레이어에게 피해를 줄 수 있습니다.
    + 메서드: attack()
    
  + Enemy: 적 캐릭터의 AI 및 행동 패턴.
    + 메서드: draw(), update(), attack()

  + Boss: 보스 캐릭터의 AI 및 특별 공격 패턴.
    + 메서드: draw(), update(), special_attack()

  + Item: 아이템의 속성과 효과 정의.
    + 메서드: draw(), use()

  + Dungeon: 던전의 구조 및 생성 알고리즘.
    + 메서드: generate(), draw()

+ 키보드 입력 처리
  + wasd : 캐릭터 이동
  + space : 구르기
  + j : 바라보는 방향으로 무기 공격 실행
    
+ 개발 기법
  + 랜덤 맵 생성: 던전을 랜덤하게 생성하는 알고리즘.
  + 상태 관리: 플레이어와 적의 상태를 효율적으로 관리하는 시스템.


+ 게임 프레임워크
  + 기본 게임 루프를 사용
  + 이미지 출력, 입력 처리, 충돌 검사.


+ 일정
  + 1주차: 기본 구조 구현, 리소스 수집
  + 2주차: 캐릭터 구현
  + 3주차: 무기 시스템 구현
  + 4주차: 일반 몬스터 구현
  + 5주차: 랜덤 던전 생성 알고리즘 개발.
  + 6주차: 보스 및 능력 시스템 구현.
  + 7주차: 테스트 및 버그 수정.



+ 진행 상황 업데이트


+ 1차 발표 영상
  + YouTube link  <https://youtu.be/zMZsBIEwkS4>

+ 1차 발표 전까지의 활동 정리
  + 게임 컨셉 확정
  + 게임 리소스 탐색
