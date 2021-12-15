if __name__ == '__main__':
	t = int(input())
	for i in range(t):
		s = input()
		if s == s[::-1]:
			print('yes')
		else:
			print('no')

		