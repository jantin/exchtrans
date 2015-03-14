#What each table does

log\_session
  * only logs the session when the moderator has explicitly started it.
  * records start and end time plus timeStamp which is the same as startTime
  * sid - session id
  * eid - experiment id

log\_participants
  * sid - session\_id
  * participantName - looks like date plus some unique identifier, unclear where the identifier comes from.
  * cumulativePoints - does not ever update
  * timestamp - unclear when this actually gets set

log\_component
stores all the components for each session
  * sid - session\_id
  * cid - component\_id
  * component index - unclear if the is the ordering of each component

log\_matcher
  * We think this table handles recording who decides what type of exchange is going to occur when there is an option for the players to choose between two or more types of exchange.

log\_nex
  * no initial offer is recorded
  * offer is recorded from the perspective of the receiver and they are not recorded until the offer is acted upon by the receiver.  For example, the receiver presses "counter offer"
  * End round was clicked.
    * 'outcome' recorded endedRound
    * on the confirmatory page, participant clicked 'no'
    * 'outcome' still showed endedRound
    * participant clicked counteroffer and submitted it.
    * 'outcome' erased endedRound and replaced it with counterOffer
    * should have recorded 'considered\_end\_round'
    * should have recorded 'canceled\_end\_round'
    * then recorded 'counterOffer'

  * ANYTIME SOMETHING PASSES THROUGH THE SERVER IT SHOULD BE RECORDED
  * offerIndex records the counteroffers as one index ID, but when the participant clicks 'Accept' it records it in the current index ID.  The participant to then receives the Accepted Offer message (the one who made the last counter offer) then gets a message whose outcome is recorded as the next offerIndex id.

  * pretty sure the column 'initiatedOffer' in table 'log\_nex' is wrong, but should be sure to confirm before editing.

log\_rex
  * declinedToMakeOffer - recorded a 1 (true) when in fact both users had made an offer.