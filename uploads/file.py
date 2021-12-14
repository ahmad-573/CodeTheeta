if __name__ == '__main__':
	t = int(input())
	for i in range(t):
		ans = ''
		n,s = input().split()
		n = int(n)
		for j in range(n):
			if s[j] != s[n-j-1]:
				ans = 'No'


		if ans == '':
			ans = 'Yes'
		print(ans)