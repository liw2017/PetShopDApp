const Petshop = artifacts.require('./Petshop.sol')


contract('Petshop', ([deployer,seller,buyer]) => {
  let petshop

  before(async () => {
    petshop = await Petshop.deployed()
  })

  describe('deployment', async () => {
    it('deploys successfully', async () => {
      const address = await petshop.address
      assert.notEqual(address, 0x0)
      assert.notEqual(address, '')
      assert.notEqual(address, null)
      assert.notEqual(address, undefined)
    })
  })

  describe('pets', async () => {
    let result, petCount

    before(async () => {
      result = await petshop.createPet('Cat','Shorthair', 1,'Toronto', 'picture','1000000000',{from: seller})
      petCount = await petshop.petCount()
    })

    it('creates pets', async () => {
      // SUCCESS
      assert.equal(petCount, 1)
      const event = result.logs[0].args
      assert.equal(event.id.toNumber(),petCount.toNumber(),'id is correct')
      assert.equal(event.name,'Cat','name is correct')
      assert.equal(event.breed,'Shorthair','brend is correct')
      assert.equal(event.age,1,'age is correct')
      assert.equal(event.location,'Toronto','location is correct')
      assert.equal(event.picture,'picture','picture is correct')
      assert.equal(event.price,'1000000000','price is correct')
      assert.equal(event.owner,seller,'owner is correct')
      assert.equal(event.purchased,false,'purchaced is correct')

    })


    it('sells pets', async () => {
      //Track seller balance before purchase
      let oldSellerBalance
      oldSellerBalance = await web3.eth.getBalance(seller)
      oldSellerBalance = new web3.utils.BN(oldSellerBalance)
      //SUCCESS
      result = await petshop.purchasePet(petCount, { from: buyer, value: web3.utils.toWei('1', 'Ether')})
      //Check logs
      const event = result.logs[0].args
      assert.equal(event.id.toNumber(),petCount.toNumber(),'id is correct')
      assert.equal(event.name,'Cat','name is correct')
      assert.equal(event.breed,'Shorthair',' is correct')
      assert.equal(event.age,1,' is correct')
      assert.equal(event.location,'Toronto',' is correct')
      assert.equal(event.picture,'picture',' is correct')
      assert.equal(event.price,'1000000000','price is correct')
      assert.equal(event.owner,buyer,'owner is correct')
      assert.equal(event.purchased,true,'purchaced is correct')
      //Check seller received funds
      let newSellerBalance
      newSellerBalance = await web3.eth.getBalance(seller)
      newSellerBalance = new web3.utils.BN(newSellerBalance)

      let price
      price = web3.utils.toWei('1','Ether')
      price = new web3.utils.BN(price)

      const expectedBalance = oldSellerBalance.add(price)

      assert.equal(newSellerBalance.toString(),expectedBalance.toString())


    })
  })
})
