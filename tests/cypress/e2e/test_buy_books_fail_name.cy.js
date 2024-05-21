describe('buy book lowercase name', () => {
  it('buy books', () => {
    cy.visit('http://localhost:8080')
    cy.contains("Explore books").click()

    cy.contains("JavaScript - The Good Parts").parent().parent().parent().contains("View").click()

    cy.get('input').clear()
    cy.get('input').type('2')

    cy.contains("Checkout").click()

    cy.get('input[id="name"]').type('karl')
    cy.get('input[id="contact"]').type('email@email.com')

    cy.get('input[id="street"]').type('street123')
    cy.get('input[id="city"]').type('Tartu')
    cy.get('input[id="state"]').type('Tartu maakond')
    cy.get('input[id="zip"]').type('11542')
    cy.get('select[id="country"]').select('Estonia')

    cy.get('textarea[id="userComment"]').type('newcomment123')

    cy.get('input[id="creditCardNumbe"]').type('46721873621')
    cy.get('input[id="creditCardExpirationDate"]').type('09/25')
    cy.get('input[id="creditCardCVV"]').type('420')

    cy.get('input[id="termsAndConditions"]').click()

    cy.contains("Submit").click()
    cy.contains("Transaction Rejected")  // rejected
  })
})
