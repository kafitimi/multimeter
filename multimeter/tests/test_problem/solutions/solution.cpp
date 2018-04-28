#include <iostream>
#include <cstdio>
#include <cmath>
#include <algorithm>
#include <set>
#include <map>
#include <cstdlib>

using namespace std;

const long long MAXN = 1e4 + 5;
const long long MAXK = 105;
const long long INF = 1e10 + 5;

long long n, k, res = INF;
long long dp[MAXN][2 * MAXK];
long long a[MAXN];

void foo(long long x)
{
	for (long long i = 0; i < n; i++)
		for (long long j = 0; j <= 2 * k; j++) dp[i][j] = INF;

	dp[x][0] = a[x];
	for (long long i = x + 1; i < n; i++)
	{
		for (long long j = 0; j <= 2 * k; j++) dp[i][0] = min(dp[i][0], dp[i - 1][j] + a[i]);
		for (long long j = 1; j <= 2 * k; j++) dp[i][j] = min(dp[i][j], dp[i - 1][j - 1]);
	}

	for (long long i = 0; i <= k; i++) res = min(res, dp[n - 1][i]);
}

int main()
{
	freopen("fire.in", "r", stdin);
	freopen("fire.out", "w", stdout);

	cin >> n >> k;

	for (long long i = 0; i < n; i++) cin >> a[i];

	for (long long i = 0; i <= k && i < n; i++) foo(i);

	cout << res;

	return 0;
}
