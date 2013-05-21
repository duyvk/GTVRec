# -*- coding: utf8 -*-

VIETNAMESE_RULES = {
    "oà":"òa",
    "oá":"óa",
    "oả":"ỏa",
    "oã":"õa",
    "oạ":"ọa",
    "oè":"òe",
    "oé":"óe",
    "oẻ":"ỏe",
    "oẽ":"õe",
    "oẹ":"ọe",
    "uỳ":"ùy",
    "uý":"úy",
    "uỷ":"ủy",
    "uỹ":"ũy",
    "uỵ":"ụy",
}

def normalize_vietnamese(text):
    if text:
        syllables = text.strip().lower().split()
        for i,syllable in enumerate(syllables):
            for k,v in VIETNAMESE_RULES.iteritems():
                if syllable.find(k) >= 0:
                    syllable = syllable.replace(k, v)
                    syllables[i] = syllable
                    break
        text = ' '.join(syllables)
    return text
