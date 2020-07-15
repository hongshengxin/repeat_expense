from requests import get


sentence = '明天下午三点下雨'
html1 = get('http://localhost:6002/time?sentence={}'.format(sentence)).json()
print(html1)