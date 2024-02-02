CREATE TABLE finished (
    qid INT,
    username VARCHAR(255),
    date DATE, -- day precision
    PRIMARY KEY (qid, username, date),
    INDEX idx_qid (qid),
    INDEX idx_username (username),
    INDEX idx_date (date)
) ENGINE=InnoDB;  -- Assuming InnoDB as the storage engine, you can adjust as needed.

CREATE TABLE batches (
    index PRIMARY KEY INT,
    qid INT NOT NULL,
    count INT NOT NULL,
    to_be_matched INT NOT NULL, -- this is the total cirrussearch results for the batch currently missing after this batch has finished in QS
    timestamp TIMESTAMP NOT NULL,
    PRIMARY KEY (index),
    INDEX idx_qid (qid)
) ENGINE=InnoDB;
