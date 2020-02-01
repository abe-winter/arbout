create extension if not exists "uuid-ossp";

create table cases (
  caseid uuid primary key default uuid_generate_v4(),
  email_hash bytea, -- using global salt so this can be looked up
  password_salt bytea,
  password_hash bytea,
  counterparty text,
  counterparty_domain text,
  issue_category text, -- broad category of the dispute
  issue text,
  real_id_hash bytea, -- using global salt so it can be crossed in the escrow DB
  incident_date date,
  dispute_date date,
  file_date date,
  arbitration_date date,
  sought_dollars int,
  settlement_dollars int,
  subjective_fair boolean,
  subjective_inmyfavor boolean,
  submitter_initiated boolean,
  arbitration_agency text,
  arbitration_agency_domain text,
  submitter_choose_agency text, -- (yes, yes_list, no)
  arbitration_state text, -- two-digit state
  draft_contract boolean, -- did submitter have a role in drafting the contract
  terms_link text, -- url to terms of service / contract
  affirm text, -- affirmation text uploaded by user
  removed boolean not null default false,
  created timestamp not null default now(),
  modified timestamp not null default now()
);

create index cases_real_id_hash on cases (real_id_hash);
