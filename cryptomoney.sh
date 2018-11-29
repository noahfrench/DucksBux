#!/bin/bash

# the first command-line parameter is in $1, the second in $2, etc.

case "$1" in

    name) python3 -c "import cmoney; cmoney.name()"
	  # additional parameters provided: (none)
	  ;;

    genesis) python3 -c "import cmoney; cmoney.genesis()"
	     # additional parameters provided: (none)
             ;;

    generate) python3 -c "import cmoney; cmoney.generate()" $2
	      # additional parameters provided: the wallet file name
              ;;

    address) python3 -c "import cmoney; print(cmoney.address())" $2
	     # additional parameters provided: the file name of the wallet
	     ;;

    fund) python3 -c "import cmoney; cmoney.fund()" $2 $3 $4
	  # additional parameters provided: destination wallet
	  # address, the amount, and the transaction file name
          ;;

    transfer) python3 -c "import cmoney; cmoney.transfer()" $2 $3 $4 $5
	      # additional parameters provided: source wallet file
	      # name, destination address, amount, and the transaction
	      # file name
	      ;;

    balance) python3 -c "import cmoney; cmoney.balance()" $2
	     # additional parameters provided: wallet address
	     ;;

    verify) python3 -c "import cmoney; cmoney.verify()" $2 $3
	    # additional parameters provided: wallet file name,
	    # transaction file name
	    ;;

    createblock) python3 -c "import cmoney; cmoney.createblock()"
		 # additional parameters provided: (none)
		 ;;
    
    validate) python3 -c "import cmoney; cmoney.validate()"
	      # additional parameters provided: (none)
	      ;;

    *) echo Unknown function: $1
       ;;

esac