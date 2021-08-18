# BitcoinBot
Bitcoin trader using the Coinbase Pro API

This bitcoin bot keeps track of previous bids/asks using a pkl file to always buy/sell according to a set threshold for profit. This Bot is optimal for a sideways market.

## Command Line
The bot can be controlled from a command line menu since it **spawns off another thread.**
There are 6 commands:
```python
start
```
Begins the trading algorithm.
```python
stop
```
Halts trading.
```python
bids
```
View current bids
```python
asks
```
View current asks
```python
account
```
View account balance
```python
quit
```
End program and save pkl files
