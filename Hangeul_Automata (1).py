import sys

# 자모 리스트
CHOSUNG_LIST = [
    'ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ',
    'ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
]
JUNGSUNG_LIST = [
    'ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ',
    'ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'
]
JONGSUNG_LIST = [
    '', 'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ',
    'ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
]

DOUBLE_JONG_LIST = [
    ('ㄱ', 'ㅅ', 'ㄳ'),
    ('ㄴ', 'ㅈ', 'ㄵ'),
    ('ㄴ', 'ㅎ', 'ㄶ'),
    ('ㄹ', 'ㄱ', 'ㄺ'),
    ('ㄹ', 'ㅁ', 'ㄻ'),
    ('ㄹ', 'ㅂ', 'ㄼ'),
    ('ㄹ', 'ㅅ', 'ㄽ'),
    ('ㄹ', 'ㅌ', 'ㄾ'),
    ('ㄹ', 'ㅍ', 'ㄿ'),
    ('ㄹ', 'ㅎ', 'ㅀ'),
    ('ㅂ', 'ㅅ', 'ㅄ')
]

DOUBLE_JUNG_LIST = [
    ('ㅗ', 'ㅏ', 'ㅘ'),
    ('ㅗ', 'ㅐ', 'ㅙ'),
    ('ㅗ', 'ㅣ', 'ㅚ'),
    ('ㅜ', 'ㅓ', 'ㅝ'),
    ('ㅜ', 'ㅔ', 'ㅞ'),
    ('ㅜ', 'ㅣ', 'ㅟ'),
    ('ㅡ', 'ㅣ', 'ㅢ')
]

# 상태 초기화
def reset_state():
    return {
        'output': [],
        'cho': '',
        'jung': '',
        'jong': '',
        'state': '초성'
    }

# 글자 조합
def combine_jamos(cho, jung, jong=''):
    cho_idx = CHOSUNG_LIST.index(cho)
    jung_idx = JUNGSUNG_LIST.index(jung)
    jong_idx = JONGSUNG_LIST.index(jong) if jong else 0
    return chr(0xAC00 + 588 * cho_idx + 28 * jung_idx + jong_idx)

# 이중 중성 처리
def merge_double_jung(j1, j2):
    return DOUBLE_JUNG.get((j1, j2), None)
    
# 이중 종성 처리
def normalize_jong(jong):
    if jong in DOUBLE_JONG:
        return DOUBLE_JONG[jong]
    return jong
    
# 글자 출력 및 상태 초기화
def flush(state):
    result = ''

    if state['cho'] and state['jung']:
        jong = normalize_jong(state['jong']) if state['jong'] else ''
        result = combine_jamos(state['cho'], state['jung'], jong)
    elif state['jung']:
        result = state['jung']
    elif state['cho']:
        result = state['cho']
    
    # 상태 초기화
    state['cho'] = ''
    state['jung'] = ''
    state['jong'] = ''
    state['state'] = '초성'
    
    return result

# 숫자인지 확인
def is_number(char):
    return char.isdigit()

def is_hangul_syllable(char):
    return 0xAC00 <= ord(char) <= 0xD7A3


def decompose(syllable):
    if not is_hangul_syllable(syllable):
        return syllable, '', ''
    
    code = ord(syllable) - 0xAC00
    cho = code // 588
    jung = (code % 588) // 28
    jong = code % 28
    return CHOSUNG_LIST[cho], JUNGSUNG_LIST[jung], JONGSUNG_LIST[jong]

def compose(cho, jung, jong=''):
    if cho not in CHOSUNG_LIST or jung not in JUNGSUNG_LIST:
        return cho + jung + jong  # 비정상 조합은 그냥 이어 붙임
    
    cho_index = CHOSUNG_LIST.index(cho)
    jung_index = JUNGSUNG_LIST.index(jung)
    jong_index = JONGSUNG_LIST.index(jong) if jong in JONGSUNG_LIST else 0
    
    code = 0xAC00 + (cho_index * 588) + (jung_index * 28) + jong_index
    return chr(code)

DOUBLE_JUNG = {(a , b): c for a, b, c in DOUBLE_JUNG_LIST}
DOUBLE_JONG = {a + b: c for a, b, c in DOUBLE_JONG_LIST}

# 역조합용 딕셔너리 (백스페이스 처리에 사용)
REVERSE_DOUBLE_JUNG = {c: (a, b) for a, b, c in DOUBLE_JUNG_LIST}
# 역조합을 이용해서 이중 중성을 분해한다.
REVERSE_DOUBLE_JONG = {c: (a, b) for a, b, c in DOUBLE_JONG_LIST}
# 역조합을 이용해서 이중 종성을 분해한다.

# 전체 오토마타
def automata(inputs):
    state = reset_state()

    i = 0
    while i < len(inputs):
        char = inputs[i]
        next_char = inputs[i + 1] if i + 1 < len(inputs) else None

        if char == '<':  # 백스페이스 처리
            if state['jong']:
                # 이중 종성일 경우
                if state['jong'] in REVERSE_DOUBLE_JONG:
                    first, second = REVERSE_DOUBLE_JONG[state['jong']]
                    state['jong'] = first  # 첫 자음만 남기고 나머지 삭제
                else:
                    state['jong'] = ''
            elif state['jung']:
                # 이중 모음일 경우
                if state['jung'] in REVERSE_DOUBLE_JUNG:
                    first, second = REVERSE_DOUBLE_JUNG[state['jung']]
                    state['jung'] = first  # 첫 모음만 남기고 나머지 삭제
                else:
                    state['jung'] = ''
            elif state['cho']:
                state['cho'] = ''
            elif state['output']:
                last = state['output'].pop()
                if last.isdigit():
                    pass
                elif is_hangul_syllable(last):
                    cho, jung, jong = decompose(last)
                    if jong:
                        # 이중 종성인지 확인
                        if jong in REVERSE_DOUBLE_JONG:
                            first, second = REVERSE_DOUBLE_JONG[jong]
                            state['cho'] = cho
                            state['jung'] = jung
                            state['jong'] = first
                        else:
                            state['cho'] = cho
                            state['jung'] = jung
                            state['jong'] = ''
                else:
                    # 종성이 없으면 중성 삭제
                    if jung in REVERSE_DOUBLE_JUNG:
                        first, _ = REVERSE_DOUBLE_JUNG[jung]
                        state['cho'] = cho
                        state['jung'] = first
                        state['jong'] = ''
                    else:
                        state['cho'] = cho
                        state['jung'] = ''
                        state['jong'] = ''
            i += 1
            continue

        if is_number(char):
            flushed = flush(state)
            if flushed:
                state['output'].append(flushed)
            state['output'].append(char)
            i += 1
            continue
        
        if state['state'] == '초성':
            # 1. 상태가 초성일 때 자음(= 초성)이 입력되는 경우
            if char in CHOSUNG_LIST:
                state['cho'] = char
                state['state'] = '중성'
                i += 1
            elif char in JUNGSUNG_LIST:
                # 2. 상태가 초성일 때 모음이 먼저 입력되는 경우 중 merged 되는 경우
                if next_char in JUNGSUNG_LIST: # char: 모음 next_char: 모음
                    merged = merge_double_jung(char, next_char)
                    if merged:
                        state['jung'] = merged
                        state['state'] = '종성후보'
                        i += 2
                        continue
                    else:
                        # 3. merged 되지 않는 경우
                        state['jung'] = char
                        state['state'] = '종성후보'
                        i += 1
                else: # 4. char과 next char 모두 모음이 아닌 경우
                    state['jung'] = char
                    flushed = flush(state)
                    if flushed:
                        state['output'].append(flushed)
                        state['state'] = '초성'
                        i += 1
                    continue

        elif state['state'] == '중성':
            if char in CHOSUNG_LIST:
                # 1. 자음이 들어오면 이전 것 flush 후 초성으로 저장
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['cho'] = char
                state['state'] = '중성'
                i += 1

            elif char in JUNGSUNG_LIST:
                if next_char in JUNGSUNG_LIST:
                    # 2. 이중 모음일 수 있음
                    merged = merge_double_jung(char, next_char)
                    if merged:
                        state['jung'] = merged
                        state['state'] = '종성후보'
                        i += 2
                        continue
                # 3. 이중 모음이 아님
                state['jung'] = char
                state['state'] = '종성후보'
                i += 1
                
        elif state['state'] == '종성후보':
            # 1. char과 next_char가 모두 자음일 때
            if char in JONGSUNG_LIST and next_char in JONGSUNG_LIST:
                double_jong = normalize_jong(char + next_char)
                if double_jong in JONGSUNG_LIST:
                    state['jong'] = double_jong
                    flushed = flush(state)
                    if flushed:
                        state['output'].append(flushed)
                    state['state'] = '초성'
                    i += 2
                else:
                    # 2. 이중자음 불가 → char은 종성, next_char는 초성
                    state['jong'] = char
                    flushed = flush(state)
                    if flushed:
                        state['output'].append(flushed)
                    state['state'] = '초성'
                    i += 1

            # 3. char은 자음이고 next_char는 모음 → char은 초성
            elif char in JONGSUNG_LIST and next_char in JUNGSUNG_LIST:
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['cho'] = char
                state['state'] = '중성'
                i += 1

            # 4. char과 next_char가 모두 모음일 때
            elif char in JUNGSUNG_LIST and next_char in JUNGSUNG_LIST:
                merged = merge_double_jung(char, next_char)
                if merged:
                    flushed = flush(state)
                    if flushed:
                        state['output'].append(flushed)
                    state['jung'] = merged
                    flushed = flush(state)
                    if flushed:
                        state['output'].append(flushed)
                    state['state'] = '초성'
                    i += 2
                else: 
                    # 5. char이 모음이고 next char도 모음이지만 이중모음이 안될때
                    flushed = flush(state)
                    if flushed:
                        state['output'].append(flushed)
                    state['jung'] = char
                    i += 1
                    flushed = flush(state)
                    if flushed:
                        state['output'].append(flushed)
                    state['state'] = '초성'

            # 6. char이 모음이고 next_char는 자음일 때
            elif char in JUNGSUNG_LIST and next_char in CHOSUNG_LIST:
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['jung'] = char
                i += 1
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['state'] = '초성'
            # 7. char이 단독 모음일 때,
            elif char in JUNGSUNG_LIST:
                # 예외 처리 또는 단독 출력
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['jung'] = char
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['state'] = '초성'
                i += 1
            # 8. char이 단독 자음일 때,
            elif char in CHOSUNG_LIST:
                state['jong'] = char
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['state'] = '초성'
                i += 1

    flushed = flush(state)
    if flushed:
        state['output'].append(flushed)

    return ''.join(state['output'])
    
# 메인 루프
if __name__ == '__main__':
    print("한글 오토마타 입력 모드입니다. (Ctrl + C를 누르면 종료됩니다)\n")

    try:
        while True:
            raw_input = input("입력: ")
            result = automata(raw_input)
            print("결과:", result)
    except KeyboardInterrupt:
        print("\n종료합니다.")
        sys.exit(0)