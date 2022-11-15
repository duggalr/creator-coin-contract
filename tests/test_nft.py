import pytest
import brownie


# ganache-cli --port 8545 --gasLimit 12000000 --accounts 10 --hardfork istanbul --mnemonic brownie

# PLATFORM_ADDRESS = ''

ETH_PRICE = 21.45

@pytest.fixture
def token(NFTMain, accounts):
  token_name = "RahulTest"
  token_symbol = "RT"
  token_total_supply = 30
  max_token_per_sale = 10  
  token_uri = "https://docs.soliditylang.org/"
  token_price_eth = ETH_PRICE
  token_price_gwei = token_price_eth * (10**19)  # gwei denomination
  deployer_account = accounts[0]

  return NFTMain.deploy(token_name, token_symbol, token_total_supply, max_token_per_sale, token_price_gwei, token_uri, {
    "from": deployer_account,
    "gas_price": 500000
  })


def test_token_deployment_failure(NFTMain, accounts):
  """
  Failed Deployment where total_token_supply < max_token_per_sale
  """
  token_name = "RahulTest"
  token_symbol = "RT"
  token_total_supply = 5
  max_token_per_sale = 10  
  token_uri = "https://docs.soliditylang.org/"
  token_price_eth = 0.1
  token_price_gwei = token_price_eth * (10**19)  # gwei denomination
  deployer_account = accounts[0]

  with brownie.reverts("Total Supply must be greater or equal to max token number per sale."):
    NFTMain.deploy(token_name, token_symbol, token_total_supply, max_token_per_sale, token_price_gwei, token_uri, {
      "from": deployer_account,
      "gas_price": 500000
    })


def test_owner_amount(token, accounts):
  owner_token_balance = token.balanceOf(accounts[0])
  assert owner_token_balance == 0


def test_get_token_price(token):
  token_price = token.getTokenPrice()
  assert token_price == ( ETH_PRICE * (10**19) )


def test_get_max_token_supply(token):
  max_token_supply = token.getMaxTokenSupply()
  assert max_token_supply == 30


def test_get_balance_address(token, accounts):
  assert token.balanceOf(accounts[1]) == 0


def test_get_token_total_supply(token):
  assert token.totalSupply() == 0
 

def test_success_increase_max_token_supply(token):
  token.increaseTokenSupply(50, {'gas_price': 25000})
  assert token.getMaxTokenSupply() == 50


def test_failure_increase_max_token_supply(token):
  with brownie.reverts("Max Token Supply must be >0 and greater than previous maxTokenSupply."):
    token.increaseTokenSupply(30, {'gas_price': 25000})


def test_failure_fetch_token_uri(token):
  with brownie.reverts("ERC721: invalid token ID"):
    token.tokenURI(0)
    token.tokenURI(1)
 

def test_success_safe_mint(token, accounts):
  """
  Success Case of single token mint
  """

  from_account = accounts[2]
  from_account_initial_balance = from_account.balance()

  deployer_account = accounts[0]
  deployer_account_initial_balance = deployer_account.balance()

  platform_account = accounts.add(private_key='0x3ff6c8dfd3ab60a14f2a2d4650387f71fe736b519d990073e650092faaa621fa')
  platform_account_initial_balance = platform_account.balance()

  initial_circulating_token_supply = token.totalSupply()
  initial_from_token_balance = token.balanceOf(from_account)

  initial_token_id = token.getCurrentTokenID()

  mint_amount = 1
  eth_price = ETH_PRICE
  from_account_value_amount = ( eth_price * (10**19) ) * mint_amount
  token.safeMint(mint_amount, {'value': from_account_value_amount, 'from': from_account})
  platform_fee = ( 3 * (eth_price * (10**19)) * mint_amount ) / 100
  deployer_amount = from_account_value_amount - platform_fee
  
  assert token.getCurrentTokenID() == (initial_token_id + mint_amount)
  # print(f'success-safe-mint-token-ID: { initial_token_id + mint_amount }')
  assert token.tokenURI( initial_token_id + mint_amount - 1 ) == "https://docs.soliditylang.org/"

  assert token.totalSupply() == initial_circulating_token_supply + 1
  assert token.balanceOf(from_account) == initial_from_token_balance + 1
  assert from_account.balance() == ( from_account_initial_balance - from_account_value_amount )
  assert deployer_account.balance() == ( deployer_account_initial_balance + deployer_amount )
  assert platform_account.balance() == ( platform_account_initial_balance + platform_fee )
  
  # print(f'deployer-account-balance: {accounts[0].balance()} / from-account-balance: {accounts[2].balance()} / platform-account-balance: {platform_account.balance()}')


def test_zero_token_failure_safe_mint(token, accounts):
  """
  Failure case where mint amount=0 is passed for safeMint()
  """
  from_account = accounts[2]
  from_account_initial_balance = from_account.balance()

  deployer_account = accounts[0]
  deployer_account_initial_balance = deployer_account.balance()

  platform_account = accounts.add(private_key='0x3ff6c8dfd3ab60a14f2a2d4650387f71fe736b519d990073e650092faaa621fa')
  platform_account_initial_balance = platform_account.balance()

  initial_circulating_token_supply = token.totalSupply()
  initial_from_token_balance = token.balanceOf(from_account)

  with brownie.reverts("Amount of NFTs exceeds the amount of NFTs you can purchase at a single time. Or amount requested is 0."):
    mint_amount = 0
    eth_price = ETH_PRICE
    from_account_value_amount = ( eth_price * (10**19) ) * mint_amount
    token.safeMint(mint_amount, {'value': from_account_value_amount, 'from': from_account})

 
def test_greater_max_token_sale_failure_safe_mint(token, accounts):
  """
  Failure case where mint-amount>_maxTokenPerSale; passed to safeMint()
  """
  from_account = accounts[2]
  from_account_initial_balance = from_account.balance()

  deployer_account = accounts[0]
  deployer_account_initial_balance = deployer_account.balance()

  platform_account = accounts.add(private_key='0x3ff6c8dfd3ab60a14f2a2d4650387f71fe736b519d990073e650092faaa621fa')
  platform_account_initial_balance = platform_account.balance()

  initial_circulating_token_supply = token.totalSupply()
  initial_from_token_balance = token.balanceOf(from_account)

  with brownie.reverts("Amount of NFTs exceeds the amount of NFTs you can purchase at a single time. Or amount requested is 0."):
    mint_amount = 100
    eth_price = ETH_PRICE
    from_account_value_amount = ( eth_price * (10**19) ) * mint_amount
    token.safeMint(mint_amount, {'value': from_account_value_amount, 'from': from_account})


def test_success_max_token_num_safe_mint(token, accounts):
  """
  Success case where _maxTokenPerSale is set to current max (10)
  """
  from_account = accounts[2]
  from_account_initial_balance = from_account.balance()

  deployer_account = accounts[0]
  deployer_account_initial_balance = deployer_account.balance()

  platform_account = accounts.add(private_key='0x3ff6c8dfd3ab60a14f2a2d4650387f71fe736b519d990073e650092faaa621fa')
  platform_account_initial_balance = platform_account.balance()

  initial_circulating_token_supply = token.totalSupply()
  initial_from_token_balance = token.balanceOf(from_account)

  initial_token_id = token.getCurrentTokenID()

  mint_amount = 10
  eth_price = ETH_PRICE
  from_account_value_amount = ( eth_price * (10**19) ) * mint_amount
  token.safeMint(mint_amount, {'value': from_account_value_amount, 'from': from_account})
  platform_fee = ( 3 * (eth_price * (10**19)) * mint_amount ) / 100 # add num mint here?
  deployer_amount = from_account_value_amount - platform_fee

  assert token.getCurrentTokenID() == (initial_token_id + mint_amount)
  assert token.tokenURI( initial_token_id + mint_amount - 1 ) == "https://docs.soliditylang.org/"

  assert token.totalSupply() == initial_circulating_token_supply + mint_amount
  assert token.balanceOf(from_account) == initial_from_token_balance + mint_amount
  assert from_account.balance() == ( from_account_initial_balance - from_account_value_amount )
  assert deployer_account.balance() == ( deployer_account_initial_balance + deployer_amount )
  assert platform_account.balance() == ( platform_account_initial_balance + platform_fee )
  


def test_incorrect_total_eth_sent(token, accounts):
  """
  Failure case where less eth sent to safeMint()
  """
  from_account = accounts[2]
  from_account_initial_balance = from_account.balance()

  deployer_account = accounts[0]
  deployer_account_initial_balance = deployer_account.balance()

  platform_account = accounts.add(private_key='0x3ff6c8dfd3ab60a14f2a2d4650387f71fe736b519d990073e650092faaa621fa')
  platform_account_initial_balance = platform_account.balance()

  initial_circulating_token_supply = token.totalSupply()
  initial_from_token_balance = token.balanceOf(from_account)

  initial_token_id = token.getCurrentTokenID()

  mint_amount = 2
  eth_price = 0.01  # incorrect lower eth_price
  from_account_value_amount = ( eth_price * (10**19) ) * mint_amount
  
  with brownie.reverts("Amount of ether sent not correct."):
    token.safeMint(mint_amount, {'value': from_account_value_amount, 'from': from_account})
  


def test_incorrect_total_eth_sent_two(token, accounts):
  """
  Failure case where greater eth sent to safeMint()
  """
  from_account = accounts[2]
  from_account_initial_balance = from_account.balance()

  deployer_account = accounts[0]
  deployer_account_initial_balance = deployer_account.balance()

  platform_account = accounts.add(private_key='0x3ff6c8dfd3ab60a14f2a2d4650387f71fe736b519d990073e650092faaa621fa')
  platform_account_initial_balance = platform_account.balance()

  initial_circulating_token_supply = token.totalSupply()
  initial_from_token_balance = token.balanceOf(from_account)

  initial_token_id = token.getCurrentTokenID()

  mint_amount = 2
  eth_price = 100.11  # incorrect higher eth_price
  from_account_value_amount = ( eth_price * (10**19) ) * mint_amount
  
  with brownie.reverts("Amount of ether sent not correct."):
    token.safeMint(mint_amount, {'value': from_account_value_amount, 'from': from_account})
  


def test_same_deployer_from_address(token, accounts):
  """
  Success case where the deployer of the contract mints their own token
  """
  from_account = accounts[0]
  from_account_initial_balance = from_account.balance()

  deployer_account = accounts[0]
  deployer_account_initial_balance = deployer_account.balance()

  platform_account = accounts.add(private_key='0x3ff6c8dfd3ab60a14f2a2d4650387f71fe736b519d990073e650092faaa621fa')
  platform_account_initial_balance = platform_account.balance()

  initial_circulating_token_supply = token.totalSupply()
  initial_from_token_balance = token.balanceOf(from_account)

  initial_token_id = token.getCurrentTokenID()

  mint_amount = 1
  eth_price = ETH_PRICE
  from_account_value_amount = ( eth_price * (10**19) ) * mint_amount
  token.safeMint(mint_amount, {'value': from_account_value_amount, 'from': from_account})
  platform_fee = ( 3 * (eth_price * (10**19)) * mint_amount ) / 100
  deployer_amount = from_account_value_amount - platform_fee

  assert token.getCurrentTokenID() == (initial_token_id + 1)
  assert token.tokenURI( initial_token_id + mint_amount - 1 ) == "https://docs.soliditylang.org/"

  assert token.totalSupply() == initial_circulating_token_supply + 1
  assert token.balanceOf(from_account) == initial_from_token_balance + 1
  assert from_account.balance() == ( from_account_initial_balance - from_account_value_amount + deployer_amount )
  assert platform_account.balance() == ( platform_account_initial_balance + platform_fee )


def test_multiple_safe_mint(token, accounts):
  """
  Success case where multiple tokens are minted
  """
  for _ in range(0, 2):

    from_account = accounts[2]
    from_account_initial_balance = from_account.balance()

    deployer_account = accounts[0]
    deployer_account_initial_balance = deployer_account.balance()

    platform_account = accounts.add(private_key='0x3ff6c8dfd3ab60a14f2a2d4650387f71fe736b519d990073e650092faaa621fa')
    platform_account_initial_balance = platform_account.balance()

    initial_circulating_token_supply = token.totalSupply()
    initial_from_token_balance = token.balanceOf(from_account)

    initial_token_id = token.getCurrentTokenID()
    
    mint_amount = 2
    eth_price = ETH_PRICE
    from_account_value_amount = ( eth_price * (10**19) ) * mint_amount
    token.safeMint(mint_amount, {'value': from_account_value_amount, 'from': from_account})
    platform_fee = ( 3 * (eth_price * (10**19)) * mint_amount ) / 100 # add num mint here?
    deployer_amount = from_account_value_amount - platform_fee

    assert token.getCurrentTokenID() == (initial_token_id + mint_amount)
    assert token.tokenURI( initial_token_id + mint_amount - 1 ) == "https://docs.soliditylang.org/"

    assert token.totalSupply() == initial_circulating_token_supply + mint_amount
    assert token.balanceOf(from_account) == initial_from_token_balance + mint_amount
    assert from_account.balance() == ( from_account_initial_balance - from_account_value_amount )
    assert deployer_account.balance() == ( deployer_account_initial_balance + deployer_amount )
    assert platform_account.balance() == ( platform_account_initial_balance + platform_fee )



def test_greater_max_token_supply_failure_safe_mint(token, accounts):
  """
  Failure case where mint-amount>maxTokenSupply; passed to safeMint()
  """

  current_remaining_token_supply = 30 - token.getCurrentTokenID()

  for _ in range(0, current_remaining_token_supply):

    from_account = accounts[2]
    from_account_initial_balance = from_account.balance()

    deployer_account = accounts[0]
    deployer_account_initial_balance = deployer_account.balance()

    platform_account = accounts.add(private_key='0x3ff6c8dfd3ab60a14f2a2d4650387f71fe736b519d990073e650092faaa621fa')
    platform_account_initial_balance = platform_account.balance()

    mint_amount = 1
    eth_price = ETH_PRICE
    from_account_value_amount = ( eth_price * (10**19) ) * mint_amount
    token.safeMint(mint_amount, {'value': from_account_value_amount, 'from': from_account})
    platform_fee = ( 3 * (eth_price * (10**19)) * mint_amount ) / 100
    deployer_amount = from_account_value_amount - platform_fee
      
    assert from_account.balance() == ( from_account_initial_balance - from_account_value_amount )
    assert deployer_account.balance() == ( deployer_account_initial_balance + deployer_amount )
    assert platform_account.balance() == ( platform_account_initial_balance + platform_fee )
    

  with brownie.reverts("Not enough tokens left to buy."):
    mint_amount = 3
    eth_price = ETH_PRICE
    from_account_value_amount = ( eth_price * (10**19) ) * mint_amount
    token.safeMint(mint_amount, {'value': from_account_value_amount, 'from': from_account})

