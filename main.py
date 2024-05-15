import time

import requests
import global_hotkeys
import pyperclip
import keyboard

delay = 0.5
_cache = {}


def error(msg):
    raise Exception(msg)


def get_citation(value: str, source: str = 'webpage'):
    if value in _cache:
        return _cache[value]

    params = {
        'q': value,
        'sourceId': source,
    }

    response = requests.get('https://www.mybib.com/api/autocite/search', params=params)
    if response.status_code != 200:
        error("Error getting citation")

    _cache[value] = response.json()
    return response.json()


def get_citation_text(citation, style: str = 'apa-7th-edition') -> tuple[str, str]:
    result = citation['results'][0] if len(citation['results']) > 0 else error("No results found")

    # combine { styleId: style } and result
    json_data = {
        **result,
        'styleId': style,
    }

    response = requests.post('https://www.mybib.com/api/autocite/reference', json=json_data)
    res = response.json()['result'] if response.status_code == 200 else error("Error getting citation")
    refstr = res['formattedReferenceStr']
    inrefstr = res['formattedInTextCitationStr']

    return refstr, inrefstr


def on_activate(incite: bool):
    print(f"{'in' if incite else ''}cite activated")

    # save clipboard to be restored later
    og_clip = pyperclip.paste()

    time.sleep(delay)

    # run control+c
    keyboard.press_and_release('ctrl+c')

    time.sleep(delay)

    # get clipboard
    clipboard = pyperclip.paste()

    print('clipboard:', clipboard)

    # process clipboard (get citation)
    try:
        citation = get_citation(clipboard)
        ref, inr = get_citation_text(citation)
    except:
        print('error getting citation')
        # restore clipboard
        pyperclip.copy(og_clip)
        return

    val = inr if incite else ref
    print('citation:', val)

    # push back to clipboard (formatted citation)
    pyperclip.copy(val)

    time.sleep(delay)

    # run control+v
    keyboard.press_and_release('ctrl+v')

    time.sleep(delay)

    # restore clipboard
    pyperclip.copy(og_clip)


# register the hotkey
cite_hotkey = "control + alt + c"
incite_hotkey = "control + alt + shift + c"


def on_cite_activate():
    on_activate(False)


def on_incite_activate():
    on_activate(True)


bindings = [
    [cite_hotkey, None, on_cite_activate, True],
    [incite_hotkey, None, on_incite_activate, True],
]

global_hotkeys.register_hotkeys(bindings)

global_hotkeys.start_checking_hotkeys()

print("Press Ctrl+Alt+C to get citation")
print("Press Ctrl+Alt+Shift+C to get in-text citation")

# Block
while True:
    time.sleep(0.1)