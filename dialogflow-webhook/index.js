
const { dialogflow } = require('actions-on-google')
const express = require('express')
const bodyParser = require('body-parser')
const request = require('request-promise-native')

const app = dialogflow({ debug: true })

app.intent('Default Welcome Intent - custom', (conv) => {
  const { uc, cpf } = conv.contexts.get('defaultwelcomeintent-followup').parameters
  const uri = `https://eletrobras-217518.appspot.com/?cu=${uc}&cpf=${cpf}`
  console.log(uri)

  return request(uri, { json: true, debug: true })
    .then(response => {
      const billings = response.billings.filter(bill => !bill.status.paid)
      let text

      if (billings.length > 0) {
        total = billings.reduce((acc, current) => {
          return acc + current.value
        }, 0)
        text = `Você tem ${billings.length} contas sem pagar no valor de R$ ${total}.\n\n`

        billings.forEach(bill => {
          text += `R$ ${bill.value} - ${bill.status.bill_code}`
        });
      } else {
        text = 'Todas as suas contas estão pagas'
      }

      conv.json({
        fulfillmentText: text
      })
    })
})

express()
  .use(bodyParser.json())
  .all('*', app)
  .listen(3000, () => {
    console.log('listening')
  })