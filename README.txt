Surprise!  There's nothing here!

This is n8's attempt at documenting adding a simple feature into the NEX
exchange model.

I'm trying to add a simple 'resetPoints' option to a round of NEX so that a
NEX exchange can be setup as a practice round for the participants.

Here's what I had to do:

1)  Add a new parameter to the NEX component itself:
      Add option in the NEX object:
      et/nex.py #64 & #39

      Add the option in the interface
      See line 295 in templates/nex_edit.html
      
      Save the parameter to the NEX object
      See line 240 in et/nex.py (in the nexEdit function)

2)  Noted that all of the component's parameters are stored in the
    request.session['exchangeParameters'] session variable.  So attempt to
    grab those and use them to reset the cumulative points.
    
    See #1031 in et/nex.py

That was it.  Note that even though the Bank Widget was the thing that displayed
the value of the cumulative points, I didn't have to do anything to the bank
widget code to make this work correctly.