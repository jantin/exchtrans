## Point Parameters ##
| **Name** | **Type** | **Description** |
|:---------|:---------|:----------------|
|Initial X| integer | The number of Xs given to the player for the first exchange opportunity. (Remember that it's set up that players are paired and then go through a given number of exchange opportunities.)|
|Initial Y| integer |The number of Ys given to the player for the first exchange opportunity. |
|X Value| string or integer |A formula (or just a constant) expressing the point value of each X|
|Y Value|string or integer |A formula (or just a constant) expressing the point value of each Y|
|Replenish X| integer |For each exchange opportunity after the first, but within the pairing, the player will receive this many new Xs.|
|Replenish Y| integer |For each exchange opportunity after the first, but within the pairing, the player will receive this many new Ys.|
|Clear X and Y|categorical|If set to "end of exchange opportunity", at the end of each exchange opportunity within the pairing, all the player's Xs and Ys are converted to points and added to the player's bank. After the exchange opportunity, the player will have 0X and 0Y. At the beginning of the next exchange opportunity within the pairing, each player will receive new X and Y in the amount defined in "Replenish X" and "Replenish Y." If set to "end of pairing", at the end of each exchange opportunity within the pairing, all the player's Xs and Ys are converted to points and added to the player's bank just like they are when clearing is set to "end of exchange opportunity". The difference is that the player's X and Y amounts are not reset to zero before being summed with the amounts defined in "Replenish X" and "Replenish Y."|
|Max X Request| integer |The largest number of X the player can request from the other|
|Max Y Request|integer |The largest number of Y the player can request from the other|


## Widgets ##
...

## Extra Options ##
| **Name** | **Type** | **Description** |
|:---------|:---------|:----------------|
| Non-binding | bool | If checked, participants will be able to choose whether or not to follow through on an offer. |
| Show point value | bool | Displays the contents of the "X Value" and "Y Value" parameters to the player at all times during the negotiated exchange. Not recommended for values that are no integers. (currently unimplemented) |
|Display Name |string|If a pairing has a decider, the decider is shown a list of exchange components from which to select. This is the name shown to the decider. |