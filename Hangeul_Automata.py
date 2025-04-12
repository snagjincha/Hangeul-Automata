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
DOUBLE_JONG = {
    'ㄱ': ['ㅅ'],
    'ㄴ': ['ㅈ', 'ㅎ'],
    'ㄹ': ['ㄱ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅌ', 'ㅍ', 'ㅎ'],
    'ㅂ': ['ㅅ'],
}

# 상태 초기화
def reset_state():
    return {
        'output': [],
        'cho': '',
        'jung': '',
        'jong': '',
        'state': '초성'
    }

state = reset_state()

# 글자 조합
def combine_jamos(cho, jung, jong=''):
    cho_idx = CHOSUNG_LIST.index(cho)
    jung_idx = JUNGSUNG_LIST.index(jung)
    jong_idx = JONGSUNG_LIST.index(jong) if jong else 0
    return chr(0xAC00 + 588 * cho_idx + 28 * jung_idx + jong_idx)

# 글자 출력 및 상태 초기화
def flush(state):
    result = ''
    
    if state['cho'] and state['jung']:
        result = combine_jamos(state['cho'], state['jung'], state['jong'])
    elif state['jung']:
        result = state['jung']
    elif state['cho']:
        result = state['cho']
    elif state['jong']:
        result = state['jong']
    
    state['cho'] = ''
    state['jung'] = ''
    state['jong'] = ''
    state['state'] = '초성'
    
    return result

# 숫자인지 확인
def is_number(char):
    return char.isdigit()

# 전체 오토마타
def automata(inputs):
    global state
    state = reset_state()

    for i, char in enumerate(inputs):
        next_char = inputs[i+1] if i + 1 < len(inputs) else None

        if char == '<':  # 백스페이스 처리
            if state['jong']:
                state['jong'] = ''
            elif state['jung']:
                state['jung'] = ''
            elif state['cho']:
                state['cho'] = ''
            elif state['output']:
                state['output'].pop()
            continue

        if is_number(char):
            flushed = flush(state)
            if flushed:
                state['output'].append(flushed)
            state['output'].append(char)
            continue

        if state['state'] == '초성':
            if char in CHOSUNG_LIST:
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['cho'] = char
                state['state'] = '중성'
            elif char in JUNGSUNG_LIST:
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['jung'] = char
                state['state'] = '초성'

        elif state['state'] == '중성':
            if char in JUNGSUNG_LIST:
                state['jung'] = char
                state['state'] = '종성후보'
            elif char in CHOSUNG_LIST:
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['cho'] = char
                state['state'] = '중성'

        elif state['state'] == '종성후보':
            if char in CHOSUNG_LIST:
                if next_char in JUNGSUNG_LIST:
                    flushed = flush(state)
                    if flushed:
                        state['output'].append(flushed)
                    state['cho'] = char
                    state['state'] = '중성'
                else:
                    state['jong'] = char
                    flushed = flush(state)
                    if flushed:
                        state['output'].append(flushed)
                    state['state'] = '중성'
            elif char in JUNGSUNG_LIST:
                flushed = flush(state)
                if flushed:
                    state['output'].append(flushed)
                state['jung'] = char
                state['state'] = '초성'

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