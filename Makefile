all:
	+$(MAKE) -C airline
	+$(MAKE) -C approval-chain
	+$(MAKE) -C broadcast
	+$(MAKE) -C chat
	+$(MAKE) -C chess
	+$(MAKE) -C crowd-funding
	+$(MAKE) -C expense-pool
	+$(MAKE) -C governance
	+$(MAKE) -C onboarding
	+$(MAKE) -C option
	+$(MAKE) -C task-tracking
	+$(MAKE) -C tic-tac-toe
	+$(MAKE) -C voting
