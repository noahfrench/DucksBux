# Noah French (njf5cu)
# Source code for *quack* DucksBux *quack quack*
import sys
import rsa
import hashlib
import os
import binascii

def name():
	print("DucksBux")
	return None

def genesis():
	genFile = open("block_0.txt", "w")
	genFile.write("Duck is the common name for a large number of species in the waterfowl family Anatidae which also includes swans and geese. Ducks are divided among several subfamilies in the family Anatidae; they do not represent a monophyletic group (the group of all descendants of a single common ancestral species) but a form taxon, since swans and geese are not considered ducks.")
	genFile.close();
	print("Genesis block created in 'block_0.txt'")
	return None

def generate():
	walletName = sys.argv[1]

	# Put the public and private keys into the wallet file.
	(pubkey, privkey) = rsa.newkeys(1024)
	walletFile = open(walletName, "w")
	walletFile.write(pubkey.save_pkcs1().decode('ascii'))
	walletFile.write(privkey.save_pkcs1().decode('ascii'))
	walletFile.close()

	# Create the wallet address by taking the first 20 digits of the hash
	# of the public key
	walletAddress = str(hashlib.sha256(pubkey.save_pkcs1()).hexdigest())[:16]

	print("New wallet generated in '" + walletName + "' with signature " + walletAddress)
	return None

def address(walletFilename = "none"):
	if (walletFilename == "none"):
		walletName = sys.argv[1]
	else:
		walletName = walletFilename

	with open(walletName, mode='rb') as privatefile:
		keydata = privatefile.read()
	pubkey = rsa.PublicKey.load_pkcs1(keydata)

	walletAddress = str(hashlib.sha256(pubkey.save_pkcs1()).hexdigest())[:16]

	return walletAddress

def fund():
	source = "Bank_of_1,000_Quacks"
	destAddress = sys.argv[1]
	amount = sys.argv[2]
	statementName = sys.argv[3]

	# Make a transaction statement for the transaction
	statementFile = open(statementName, "w")
	statementFile.write("From: " + source + "\n" + "To: " + destAddress + "\n" + "Amount: " + amount)
	statementFile.close()

	print("Funded wallet " + destAddress + " with " + amount)
	return None

def transfer():
	sourceFilename = sys.argv[1]
	destAddress = sys.argv[2]
	amount = sys.argv[3]
	statementName = sys.argv[4]

	# Get the wallet address from the wallet filename
	sourceAddress = address(sourceFilename)

	# Get the private key from the sourceFilename wallet
	with open(sourceFilename, mode='rb') as privatefile:
		keydata = privatefile.read()
		privkey = rsa.PrivateKey.load_pkcs1(keydata)

	# Make transaction statement for the transaction
	statementFile = open(statementName, "w")
	transactionMessage = "From: " + sourceAddress + "\n" + "To: " + destAddress + "\n" + "Amount: " + amount + "\n"

	# Sign the transaction
	signature = str(binascii.hexlify(rsa.sign(transactionMessage.encode('ascii'), privkey, "SHA-256")).decode('ascii'))
		
	statementFile.write(transactionMessage + "\n" + signature)

	print("Transfered " + amount + " from " + sourceFilename + " to " + destAddress + " and the statement to " + statementName)

	return None

def balance(wallet = "none"):
	# Take an optional parameter so other python functions can call balance()
	if (wallet == "none"):
		walletAddress = sys.argv[1]
	else:
		walletAddress = wallet

	# Iterate through the blockchain to check blockchain balance
	blockNum = 1; # base case; start at genesis block
	blockExists = True 
	blockchainBalance = 0.0
	curBlock = "block_1.txt"
	while (blockExists):
		# If there's no block 1, break!
		if (not os.path.isfile(curBlock)):
			break
		curBlockFile = open(curBlock, "r")
		lines = curBlockFile.readlines()
		# Start at the second line, because the first one is the hash value
		lines2 = lines[1:]
		for line in lines2:
			words = line.strip().split()
			# If the walletAddress is the sender, subtract the amount from their balance
			if (words[0] == walletAddress):
				blockchainBalance -= float(words[2])
			# If the walletAddress is the sender, add the amount to their balance
			if (words[4] == walletAddress):
				blockchainBalance += float(words[2])
		blockNum += 1
		curBlock = "block_" + str(blockNum) + ".txt"
		blockExists = os.path.isfile(curBlock)

	# Calculate their ledger balance (if the ledger exists) 
	ledgerBalance = 0.0
	if (os.path.isfile("ledger.txt")):
		ledgerFile = open("ledger.txt")
		lines = ledgerFile.readlines()
		for line in lines:
			words = line.strip().split()
			if (words[0] == walletAddress):
				ledgerBalance -= float(words[2])
			if (words[4] == walletAddress):
				ledgerBalance += float(words[2])

	totalBalance = blockchainBalance + ledgerBalance

	# Only print the thing if balance was called via command line arguments 
	if (wallet == "none"):
		print("The balance for wallet " + walletAddress + " is: " + str(totalBalance))
	return totalBalance

def verify():
	sourceFilename = sys.argv[1]
	statementFilename = sys.argv[2]

	# Get the private key from the sourceFilename wallet
	with open(sourceFilename, mode='rb') as privatefile:
		keydata = privatefile.read()
		privkey = rsa.PrivateKey.load_pkcs1(keydata)

	# Get the message used to create the signature and get the alleged signature and other things
	statementFile = open(statementFilename, "r")
	lines = statementFile.readlines()
	statementFile.close()
	sourceAddress = lines[0].strip().split()[1]
	fundRequest = (sourceAddress == "Bank_of_1,000_Quacks")
	destAddress = lines[1].strip().split()[1]
	amount = lines[2].strip().split()[1]

	if fundRequest:
		allegedSig = "It's a fund request!"
	else:
		allegedSig = lines[4]

	transactionList = lines[:3]
	transactionMessage = ""
	for line in transactionList:
		transactionMessage += line

	#Calculate the theoretical signature and check it against the alleged signature
	theoreticalSig = str(binascii.hexlify(rsa.sign(transactionMessage.encode('ascii'), privkey, "SHA-256")).decode('ascii'))

	validSig = (theoreticalSig == allegedSig)

	# Check to make sure the source has enough funds
	enoughFunds = (balance(sourceAddress) - float(amount)) > 0.0

	# If valid signature and enough funds, make a record in the ledger!
	if validSig and enoughFunds:
		ledgerFile = open("ledger.txt", "a")
		ledgerFile.write(sourceAddress + " transfered " + amount + " to " + destAddress + "\n")
		ledgerFile.close()
		print("The transaction in file '" + statementFilename + "' with wallet '" + sourceFilename + "' is valid, and was written to the ledger")
	elif fundRequest:
		ledgerFile = open("ledger.txt", "a")
		ledgerFile.write(sourceAddress + " transferred " + amount + " to " + destAddress + "\n")
		ledgerFile.close()
		print("Any fund request (i.e., from Bank_of_1,000_Quacks) is considered valid; written to the ledger")

	return None

def createblock():
	# Store the filename of highest current block as currentBlock.
	# Store the filename of new block as newBlock.
	blockNum = 0;
	blockExists = True 
	while (blockExists):
		newBlock = "block_" + str(blockNum) + ".txt"
		blockExists = os.path.isfile(newBlock)
		blockNum += 1

	blockNum -= 2
	currentBlock = "block_" + str(blockNum) + ".txt"

	# Hash contents of currentBlock
	hasher = hashlib.sha256()
	with open(currentBlock, "rb") as afile:
		buf = afile.read()
		hasher.update(buf)
		hasher.update(buf)
	currentBlockHash = hasher.hexdigest()
	afile.close()

	# Add that hash to the top of the new block file
	newBlockFile = open(newBlock, "w")
	newBlockFile.write(currentBlockHash + "\n")
	newBlockFile.close()

	# Append all the contents from the ledger into the new block file
	with open("ledger.txt") as f:
		with open(newBlock, "a") as f1:
			for line in f:
				f1.write(line)
	f.close()
	f1.close()

	# Erase the contents of the ledger
	open("ledger.txt", "w").close()

	print("All transactions in the ledger moved to " + newBlock)
	return None

def validate():
	# Starting at the genesis block, take the hash of a block and make sure
	# it matches line one of the next block
	blockNum = 0;
	blockExists = True
	isValid = True 
	curBlock = "block_0.txt" # base case
	while (blockExists):
		# Hash contents of curBlock
		hasher = hashlib.sha256()
		with open(curBlock, "rb") as afile:
			buf = afile.read()
			hasher.update(buf)
			hasher.update(buf)
		curHash = hasher.hexdigest()
		afile.close()

		# Get the filename of the next block
		blockNum += 1
		curBlock = "block_" + str(blockNum) + ".txt"
		blockExists = os.path.isfile(curBlock)

		# If the next block exists, compare its first line with curHash
		if (blockExists):
			with open(curBlock) as curBlockFile:
				firstLine = curBlockFile.readline()
			curBlockFile.close()

			isValid = (firstLine.rstrip() == curHash)
			if (not isValid):
				break
	
	if (isValid):
		print("The entire blockchain is valid.")
	else:
		print("The blockchain is NOT valid!")

	return None