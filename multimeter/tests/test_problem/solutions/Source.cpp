#include <iostream>
#include <algorithm>

using namespace std;

long long a[111111];
long long ans[111111];

int n, k;

int main()
{
    freopen("fire.in", "r", stdin);
    freopen("fire.out", "w", stdout);
    cin >> n >> k;
    long long sum = 0;
    for (int i = 0; i < n; i++)
    {
        cin >> a[i];
        sum += a[i];
    }
    if (!k)
    {
        cout << sum;
        return 0;
    }
    ans[0] = a[0];
    for (int i = 0; i < n; i++)
    {
        ans[i] = 0x7fffffffffffLL;
        if (i <= k)
        {
            ans[i] = a[i];
        }
        for (int j = i - 2 * k - 1; j < i; j++)
        {
            if (j < 0)
            {
                continue;
            }
            ans[i] = min(ans[i], ans[j] + a[i]);
        }
    }
    long long mn = 0x7fffffffffffLL;
    for (int i = n - 1 - k; i < n; i++)
    {
        if (i < 0)
        {
            continue;
        }
        if (ans[i] < mn)
        {
            mn = ans[i];
        }
    }
    cout << mn;
}