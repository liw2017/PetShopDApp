pragma solidity ^0.5.0;







 
contract Petshop {
   
   







//1.petshop contract
  address[16] public adopters;
  // Adopting a pet
  function adopt(uint petId) public returns (uint) {
    require(petId >= 0 && petId <= 16);

    adopters[petId] = msg.sender;

    return petId;
  }
  // Retrieving the adopters
  function getAdopters() public view returns (address[16] memory) {
    return adopters;
  }
//petshop contract end

//2.Add and buy pets

    uint public petCount = 0;
    mapping(uint => Pet) public pets;

    //pet struct
    struct Pet{
      uint id;
      string name;
      string breed;
      uint age;
      string location;
      string picture;
      uint price;
      address payable owner;
      bool purchased;
    }

    //Event adding pet
    event PetCreated(
      uint id,
      string name,
      string breed,
      uint age,
      string location,
      string picture,
      uint price,
      address payable owner,
      bool purchased
    );

    //Eevent purchasing pet
    event PetPurchased(
      uint id,
      string name,
      string breed,
      uint age,
      string location,
      string picture,
      uint price,
      address payable owner,
      bool purchased
    );

    // Add pets
    function createPet(string memory _name, string memory _breed, uint _age, string memory _location, string memory _picture, uint _price) public {
      //Require
      require(bytes(_name).length > 0);
      require(bytes(_breed).length > 0);
      require(_age > 0);
      require(bytes(_location).length > 0);
      require(bytes(_picture).length > 0);
      require(_price > 0);
      //count pet number
      petCount ++;
      //Create the pet
      pets[petCount] = Pet(petCount, _name, _breed, _age, _location, _picture, _price, msg.sender, false);
      //Trigger an event
      emit PetCreated(petCount, _name, _breed, _age, _location, _picture, _price, msg.sender, false);
    }

    //Purchase Pets
    function purchasePet(uint _id) public payable {
      //Fetch the pet
      Pet memory _pet = pets[_id];
      //Fetch the owner
      address payable _seller = _pet.owner;
      //require a valid pet id
      require(_pet.id > 0 && _pet.id <= petCount);
      //require enough Ether in the transaction
      require(msg.value >= _pet.price);
      // require that the pet has not been purchased already
      require(!_pet.purchased);
      // Require that the buyer is not the seller
      require(_seller != msg.sender);
      // Transfer ownership to the buyer
      _pet.owner = msg.sender;
      // Mark as purchased
      _pet.purchased = true;
      // Update the pet
      pets[_id] = _pet;
      // Pay the seller by sending Ether
      address(_seller).transfer(msg.value);
      // Trigger an event
      emit PetCreated(petCount, _pet.name, _pet.breed, _pet.age, _pet.location, _pet.picture, _pet.price, msg.sender, true);
    }


//3.Donation
    string public functionCalled;

    //function allowing an ether payment to the contract address
      function receiveEther() external payable {
      functionCalled = "receiveEther";
    }

    //fallback function allowing an ether payment to the contract address
      function() external payable {
      functionCalled = "fallback";
    }



//4.election contract


  // Model a Candidate
  struct Candidate {
      uint id;
      string name;
      uint voteCount;
  }

  // Store accounts that have voted
  mapping(address => bool) public voters;
  // Store Candidates
  // Fetch Candidate
  mapping(uint => Candidate) public candidates;
  // Store Candidates Count
  uint public candidatesCount;

  // voted event
  event votedEvent (
      uint indexed _candidateId
  );

  constructor () public {
    addCandidate("petid 0");
    addCandidate("petid 1");
    addCandidate("petid 2");
    addCandidate("petid 3");
    addCandidate("petid 4");
    addCandidate("petid 5");
    addCandidate("petid 6");
    addCandidate("petid 7");
    addCandidate("petid 8");
    addCandidate("petid 9");
    addCandidate("petid 10");
    addCandidate("petid 11");
    addCandidate("petid 12");
    addCandidate("petid 13");
    addCandidate("petid 14");
    addCandidate("petid 15");
    functionCalled = "constructor";
  }

  function addCandidate (string memory _name) private {
    candidatesCount ++;
    candidates[candidatesCount] = Candidate(candidatesCount, _name, 0);
      
  }

  function vote (uint _candidateId) public {
      // require that they haven't voted before
      require(!voters[msg.sender]);

      // require a valid candidate
      require(_candidateId > 0 && _candidateId <= candidatesCount);

      // record that voter has voted
      voters[msg.sender] = true;

      // update candidate vote Count
      candidates[_candidateId].voteCount ++;

      // trigger voted event
      emit votedEvent(_candidateId);
  }


//election contract end





}