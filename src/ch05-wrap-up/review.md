# 개념 되짚기

1부와 2부에서 설명한 네 가지 핵심 개념 — tool calling, agent loop, plan → write → test → run, memory / context window — 이 튜토리얼의 4부 실제 실행 기록에서 어떻게 나타났는지 간략히 되짚어 봅니다. 이론으로 접했던 것들이 실제 JSONL 이벤트와 터미널 출력 속에서 어떻게 구체화되는지 확인하는 과정입니다.

---

## tool calling — 에이전트가 환경을 바꾼 순간들

1부에서 tool calling을 "LLM이 텍스트 대신 구조화된 툴 호출을 출력해 환경에 직접 행동을 지시하는 메커니즘"으로 정의했습니다. 이번 실행에서 그 메커니즘이 가장 직접적으로 드러난 것은 에이전트가 `printf`나 heredoc(`cat > FILE <<'EOF'`)을 사용해 파일을 만들 때였습니다.

에이전트는 file_editor 툴 대신 bash 셸 명령으로 파일을 작성했습니다(그 이유는 부록 B의 REAL-04를 보세요). `TerminalAction`이 각 파일 생성 명령에 해당하고, `TerminalObservation`이 셸의 응답(종료 코드, stdout, stderr)을 담습니다. task3-parser.jsonl에서 4번의 빌드 시도와 각각의 컴파일러 오류 출력이 TerminalObservation으로 기록된 것이 이 패턴의 가장 선명한 사례입니다.

tool calling이 없었다면 에이전트는 "Parser.fsy를 이렇게 고쳐 보세요"라는 텍스트만 출력할 수 있었을 것입니다. tool calling이 있기 때문에 에이전트는 파일을 직접 작성하고, 빌드를 실행하고, 오류를 읽고, 수정하는 과정을 자율적으로 반복할 수 있었습니다.

---

## agent loop — 행동 → 관찰 → 다음 행동

agent loop의 구조(프롬프트 준비 → LLM 호출 → 행동 실행 → 관찰 기록 → 반복)가 가장 생생하게 보이는 곳은 역시 task3-parser.jsonl의 오류-수정 사이클입니다.

에이전트는 네 번의 빌드 오류를 차례로 받아들이면서, 각 오류 메시지를 다음 루프의 입력으로 삼아 접근 방식을 수정했습니다.

```
이벤트 10: dotnet build → FSY000: at least one %start declaration is required
이벤트 16: dotnet build → Parser.fsy(16,7): error parse error
이벤트 20: dotnet build → Parser.fsy(16,7): error parse error
이벤트 26: dotnet build → FS0039: 'LexBuffer<_>' does not define 'FromText'
이벤트 30: dotnet build → calc net10.0 성공 (0.7초)
```

사람이 "이제 다음 오류로 가라"고 지시한 것이 아닙니다. 에이전트가 컴파일러 출력을 관찰하고, 스스로 진단하고, 코드를 수정하고, 다시 빌드를 실행했습니다. 이것이 1부에서 설명한 agent loop의 자율성이 실제로 동작하는 모습입니다.

---

## plan → write → test → run — 5개 태스크의 분해 구조

1부에서 소개한 탐색(Explore) → 분석(Analyze) → 구현(Implement) → 검증(Verify) 방법론은 이번 실행에서 5개의 태스크로 구체화됐습니다.

```
task1-scaffold   프로젝트 구조 생성 (Explore + Implement)
task2-lexer      Lexer.fsl 작성 (Implement)
task3-parser     Parser.fsy 작성 + 4번 빌드 실패 → 자가 수정 (Implement + Verify)
task4-evaluator  Program.fs 작성 (Implement)
task5-buildtest  전체 빌드 + 3가지 테스트 케이스 검증 (Verify)
```

각 태스크는 별도의 OpenHands 헤드리스 호출로 실행됐습니다. 이렇게 분리하면 한 태스크가 실패해도 이전 태스크의 결과가 보존됩니다. task3에서 네 번의 오류를 거친 것이 전체 실행에 미친 영향은 1분 17초의 추가 시간뿐이었습니다.

검증 단계가 단순한 확인이 아니라 자가 수정의 트리거가 된다는 점이 핵심입니다. task3에서 `%start` 선언 오류가 곧바로 수정 행동으로 이어진 것이 그 예입니다. 검증(Verify)과 구현(Implement)이 에이전트 루프 안에서 하나의 연속적인 과정으로 통합됩니다.

---

## memory / context window — 오류 맥락이 수정까지 이어졌다

task3에서 에이전트가 네 번의 오류를 연속으로 처리할 수 있었던 것은, 이전 오류의 내용이 다음 루프 반복에서도 컨텍스트로 유지됐기 때문입니다.

1부에서 설명한 EventLog의 append-only 구조가 바로 이 역할을 합니다. 첫 번째 시도에서 발생한 `FSY000` 오류가 이벤트 10에 기록되면, 그 오류 메시지는 이벤트 11 이후의 모든 LLM 호출의 입력에 포함됩니다. 에이전트가 "아까 %start를 빠뜨렸으니 이번에는 넣어야 한다"고 추론할 수 있는 것은 이 구조 덕분입니다.

이번 실행은 비교적 짧았기 때문에(태스크당 평균 수십 초, 전체 약 6분) CondensationSummaryEvent(컨텍스트 압축)가 발동되는 상황에는 이르지 않았습니다. 하지만 더 큰 코드베이스나 더 긴 작업에서는 EventLog가 압축 임계값(기본 80개 이벤트)을 넘으면 이 압축이 자동으로 동작합니다.

---

## 되짚어 보며

네 가지 개념은 서로 분리된 기능이 아닙니다. tool calling이 에이전트에게 환경을 바꿀 수 있는 손과 발을 주고, agent loop가 그 손발을 반복적으로 사용하는 구조를 만들며, plan → write → test → run 방법론이 그 반복이 목표를 향해 나아가도록 방향을 잡고, memory가 이전 단계의 정보를 다음 단계까지 이어줍니다.

F# 계산기 빌드는 규모가 작은 예제였지만, 이 네 가지 원리가 어떻게 함께 작동하는지를 보여주기에는 충분했습니다. 같은 원리가 더 큰 코드베이스, 더 복잡한 작업, 더 강력한 모델에 그대로 적용됩니다.
