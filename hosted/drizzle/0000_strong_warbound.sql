CREATE TABLE `pp_batches` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`digest` text NOT NULL,
	`created` text NOT NULL,
	`undone` integer DEFAULT 0 NOT NULL,
	`duplicates` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE `pp_budgets` (
	`owner` text NOT NULL,
	`month` text NOT NULL,
	`category` text NOT NULL,
	`amount` integer NOT NULL,
	PRIMARY KEY(`owner`, `month`, `category`)
);
--> statement-breakpoint
CREATE TABLE `pp_goals` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`owner` text NOT NULL,
	`title` text NOT NULL,
	`target` integer NOT NULL,
	`saved` integer DEFAULT 0 NOT NULL,
	`date` text
);
--> statement-breakpoint
CREATE TABLE `pp_invoices` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`owner` text NOT NULL,
	`customer` text NOT NULL,
	`taxable` integer NOT NULL,
	`rate` integer NOT NULL,
	`total` integer NOT NULL,
	`status` text DEFAULT 'draft' NOT NULL
);
--> statement-breakpoint
CREATE TABLE `pp_limits` (
	`key` text PRIMARY KEY NOT NULL,
	`count` integer NOT NULL,
	`expires` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `pp_movements` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`owner` text NOT NULL,
	`goal` integer NOT NULL,
	`amount` integer NOT NULL,
	`note` text NOT NULL,
	`created` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `pp_state` (
	`key` text PRIMARY KEY NOT NULL,
	`value` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `pp_transactions` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`owner` text NOT NULL,
	`description` text NOT NULL,
	`amount` integer NOT NULL,
	`category` text NOT NULL,
	`date` text NOT NULL,
	`direction` text NOT NULL,
	`batch` text,
	`line` integer,
	`archived` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE INDEX `pp_tx_owner_date` ON `pp_transactions` (`owner`,`date`);--> statement-breakpoint
CREATE UNIQUE INDEX `pp_batch_line` ON `pp_transactions` (`batch`,`line`);
--> statement-breakpoint
CREATE TRIGGER pp_import_duplicate BEFORE INSERT ON pp_transactions
WHEN NEW.batch IS NOT NULL AND (SELECT duplicates FROM pp_batches WHERE id=NEW.batch AND owner=NEW.owner)=0
AND EXISTS(SELECT 1 FROM pp_transactions WHERE owner=NEW.owner AND archived=0 AND description=NEW.description AND amount=NEW.amount AND date=NEW.date AND direction=NEW.direction)
BEGIN SELECT RAISE(ABORT,'POSSIBLE_DUPLICATE'); END;
