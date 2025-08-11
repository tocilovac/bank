-- SQLite
create table if not exists TRANSACTIONS (
    TRANSACTION_id integer primary key AUTOINCREMENT,
    account_id integer not null,
    type text not null check(type in ('deposit', 'withdrawal', 'transfer_in', 'transfer_out')),
    amount real not null check(amount > 0),
    balance_after real not null,
    description text,
    related_account_id integer,
    timestampt text default (datetime('now')),
    FOREIGN KEY (account_id) REFERENCES ACCOUNTS(account_id),
    FOREIGN KEY (related_account_id) REFERENCES ACCOUNTS(account_id)
);


INSERT INTO Transactions (account_id, type, amount, balance_after, description)
VALUES (1, 'deposit', 100.0, 100.0, 'Initial deposit');

