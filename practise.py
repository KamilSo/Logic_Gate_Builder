txt = 'pinkfairyarmadillo'
index,word_list = ([n for n in range(len(txt)) if txt[n] in ['a','e','i','o','u']],[letter for letter in txt])
for int_index,i in enumerate(index):
	word_list[index[0]], word_list[index[-1]] = word_list[index[-1]],word_list[index[0]]
	del index[0], index[-1]
print(*word_list)
