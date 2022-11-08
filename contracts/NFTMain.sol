// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "OpenZeppelin/openzeppelin-contracts@4.7.3/contracts/token/ERC721/ERC721.sol";
import "OpenZeppelin/openzeppelin-contracts@4.7.3/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.7.3/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "OpenZeppelin/openzeppelin-contracts@4.7.3/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.7.3/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.7.3/contracts/utils/Counters.sol";
import "OpenZeppelin/openzeppelin-contracts@4.7.3/contracts/utils/math/SafeMath.sol";



/// @custom:security-contact creatorcoin42@gmail.com
contract NFTMain is ERC721, ERC721Enumerable, ERC721URIStorage, ERC721Burnable, Ownable {
    using SafeMath for uint256;

    using Counters for Counters.Counter;

    Counters.Counter private _tokenIdCounter;

    /// Main Public Key
    address private _platformAddress = 0x1CEE82EEd89Bd5Be5bf2507a92a755dcF1D8e8dc;
    uint256 private _platformFee = 3;

    /// Token Metadata
    uint256 private _maxTokenSupply;
    uint256 private _maxTokenPerSale;
    uint256 private _tokenPrice;  // will be in ETH denomination 
    string private _baseTokenURI;
    address private _deployerAddress;


    constructor(string memory tokenName, string memory tokenSymbol, uint256 totalSupply, uint256 maxNumPerSale, uint256 _userTokenPrice, string memory _userTokenURI) ERC721(tokenName, tokenSymbol) {

        require(maxNumPerSale > 0, "Max Token Per Sale must be >0.");
        require(totalSupply > 0, "Max Token Supply must be >0.");
        require( totalSupply >= maxNumPerSale, "Total Supply must be greater or equal to max token number per sale.");

        _maxTokenSupply = totalSupply;
        _maxTokenPerSale = maxNumPerSale;
        _tokenPrice = _userTokenPrice;  // will be in WEI denomination 
        _baseTokenURI = _userTokenURI;

        _deployerAddress = msg.sender;

    }


    function getTokenPrice() public view returns(uint256) {        
        return _tokenPrice;
    }

    function getMaxTokenSupply() public view returns (uint256) {
        return _maxTokenSupply;
    }

    function getCurrentTokenID() public view returns (uint256) {
        return _tokenIdCounter.current();
    }


    function _runMint(uint256 _numTokens) private {

        // Loop to mint amount requested, after the money has been transferred
        for(uint256 i = 0; i < _numTokens; i++) {
            _safeMint(msg.sender, _tokenIdCounter.current());
            _setTokenURI(_tokenIdCounter.current(), _baseTokenURI);
            _tokenIdCounter.increment();
        }

    }


    function safeMint(uint256 _numTokens) public payable {
      
        require( _numTokens > 0 && _numTokens <= _maxTokenPerSale, "Amount of NFTs exceeds the amount of NFTs you can purchase at a single time. Or amount requested is 0.");

        (bool _addBool, uint256 _totalValue) = SafeMath.tryAdd(_tokenIdCounter.current(), _numTokens);
        require(_addBool);
        require(_maxTokenSupply >= _totalValue, "Not enough tokens left to buy.");

        (bool _mulBool, uint256 _totalEthCost) = SafeMath.tryMul(_tokenPrice, _numTokens);
        require(_mulBool);
        require(msg.value == _totalEthCost, "Amount of ether sent not correct.");  // require msg.value to be exactly correct

        // "3%"-Fee, given to platform; that's why divide by 100 below
        (bool _mulBoolNew, uint256 _platformInitialCost) = SafeMath.tryMul(_platformFee, msg.value); 
        require(_mulBoolNew);
        (bool _divBool, uint256 _platformCost) = SafeMath.tryDiv(_platformInitialCost, 100);
        require(_divBool);
        (bool _subBool, uint256 _remainingValue) = SafeMath.trySub(msg.value, _platformCost);
        require(_subBool);

        // pay platform
        (bool platformSent, bytes memory platformData) = payable(_platformAddress).call{value: _platformCost}("");  // send to platform
        require(platformSent, "Failed to send Ether");

        // pay creator
        (bool sent, bytes memory data) = payable(_deployerAddress).call{value: _remainingValue}("");  // sent to creator
        require(sent, "Failed to send Ether"); 

        // TODO: 
          // vuln. to re-entranacy or other attacks? (look at ethernaut)
          // Emitting events on fund transfer? 

        _runMint(_numTokens);
 
    }


    // Callable by owner to increase supply
    function increaseTokenSupply(uint256 newSupply) public onlyOwner {

        require(newSupply > 0 && newSupply > _maxTokenSupply, "Max Token Supply must be >0 and greater than previous maxTokenSupply.");

        _maxTokenSupply = newSupply;

    }


    // The following functions are overrides required by Solidity.

    function _beforeTokenTransfer(address from, address to, uint256 tokenId)
        internal
        override(ERC721, ERC721Enumerable)
    {
        super._beforeTokenTransfer(from, to, tokenId);
    }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
    
}


 


 