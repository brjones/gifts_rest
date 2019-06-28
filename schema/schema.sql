--
-- PostgreSQL database dump
--

-- Dumped from database version 10.7 (Ubuntu 10.7-1.pgdg16.04+1)
-- Dumped by pg_dump version 10.7 (Ubuntu 10.7-1.pgdg16.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: ensembl_gifts; Type: SCHEMA; Schema: -; Owner: ensrw
--

CREATE SCHEMA ensembl_gifts;


ALTER SCHEMA ensembl_gifts OWNER TO ensrw;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: on_mapping_insert_add_default_status(); Type: FUNCTION; Schema: ensembl_gifts; Owner: ensrw
--

CREATE FUNCTION ensembl_gifts.on_mapping_insert_add_default_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   insert into ue_mapping_status (status, mapping_id) values (1, new.mapping_id);
   RETURN NEW;
END;
$$;


ALTER FUNCTION ensembl_gifts.on_mapping_insert_add_default_status() OWNER TO ensrw;

--
-- Name: on_update_current_timestamp_mapping_history(); Type: FUNCTION; Schema: ensembl_gifts; Owner: ensrw
--

CREATE FUNCTION ensembl_gifts.on_update_current_timestamp_mapping_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   NEW.time_mapped = now();
   RETURN NEW;
END;
$$;


ALTER FUNCTION ensembl_gifts.on_update_current_timestamp_mapping_history() OWNER TO ensrw;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: aap_auth_aapuser; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.aap_auth_aapuser (
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    elixir_id character varying(50) NOT NULL,
    full_name character varying(255),
    email character varying(255) NOT NULL,
    is_admin boolean NOT NULL,
    validated boolean NOT NULL
);


ALTER TABLE ensembl_gifts.aap_auth_aapuser OWNER TO ensrw;

--
-- Name: alignment; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.alignment (
    alignment_id bigint NOT NULL,
    alignment_run_id bigint NOT NULL,
    uniprot_id bigint,
    transcript_id bigint,
    mapping_id bigint,
    score1 double precision,
    report character varying(300),
    is_current boolean,
    score2 double precision
);


ALTER TABLE ensembl_gifts.alignment OWNER TO ensrw;

--
-- Name: alignment_alignment_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.alignment_alignment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.alignment_alignment_id_seq OWNER TO ensrw;

--
-- Name: alignment_alignment_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.alignment_alignment_id_seq OWNED BY ensembl_gifts.alignment.alignment_id;


--
-- Name: alignment_run; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.alignment_run (
    alignment_run_id bigint NOT NULL,
    userstamp character varying(30),
    time_run timestamp with time zone DEFAULT now(),
    score1_type character varying(30),
    report_type character varying(30),
    pipeline_name character varying(30) NOT NULL,
    pipeline_comment character varying(300) NOT NULL,
    release_mapping_history_id bigint NOT NULL,
    ensembl_release bigint NOT NULL,
    uniprot_file_swissprot character varying(300),
    uniprot_file_isoform character varying(300),
    uniprot_dir_trembl character varying(300),
    logfile_dir character varying(300),
    pipeline_script character varying(300) NOT NULL,
    score2_type character varying(30)
);


ALTER TABLE ensembl_gifts.alignment_run OWNER TO ensrw;

--
-- Name: alignment_run_alignment_run_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.alignment_run_alignment_run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.alignment_run_alignment_run_id_seq OWNER TO ensrw;

--
-- Name: alignment_run_alignment_run_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.alignment_run_alignment_run_id_seq OWNED BY ensembl_gifts.alignment_run.alignment_run_id;


--
-- Name: cv_entry_type; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.cv_entry_type (
    id bigint DEFAULT '0'::bigint NOT NULL,
    description character varying(20)
);


ALTER TABLE ensembl_gifts.cv_entry_type OWNER TO ensrw;

--
-- Name: cv_ue_label; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.cv_ue_label (
    id bigint NOT NULL,
    description character varying(40) NOT NULL
);


ALTER TABLE ensembl_gifts.cv_ue_label OWNER TO ensrw;

--
-- Name: cv_ue_status; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.cv_ue_status (
    id bigint NOT NULL,
    description character varying(20) NOT NULL
);


ALTER TABLE ensembl_gifts.cv_ue_status OWNER TO ensrw;

--
-- Name: django_migrations; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE ensembl_gifts.django_migrations OWNER TO ensrw;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.django_migrations_id_seq OWNER TO ensrw;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.django_migrations_id_seq OWNED BY ensembl_gifts.django_migrations.id;


--
-- Name: domain; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.domain (
    domain_id bigint NOT NULL,
    isoform_id bigint,
    start bigint,
    "end" bigint,
    description character varying(45)
);


ALTER TABLE ensembl_gifts.domain OWNER TO ensrw;

--
-- Name: domain_domain_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.domain_domain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.domain_domain_id_seq OWNER TO ensrw;

--
-- Name: domain_domain_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.domain_domain_id_seq OWNED BY ensembl_gifts.domain.domain_id;


--
-- Name: ensembl_gene; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.ensembl_gene (
    gene_id bigint NOT NULL,
    ensg_id character varying(30),
    gene_name character varying(255),
    chromosome character varying(50),
    region_accession character varying(50),
    mod_id character varying(30),
    deleted boolean DEFAULT false,
    seq_region_start bigint,
    seq_region_end bigint,
    seq_region_strand bigint DEFAULT '1'::bigint,
    biotype character varying(40),
    time_loaded timestamp with time zone,
    gene_symbol character varying(30),
    gene_accession character varying(30),
    source character varying(30)
);


ALTER TABLE ensembl_gifts.ensembl_gene OWNER TO ensrw;

--
-- Name: ensembl_gene_gene_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.ensembl_gene_gene_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.ensembl_gene_gene_id_seq OWNER TO ensrw;

--
-- Name: ensembl_gene_gene_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.ensembl_gene_gene_id_seq OWNED BY ensembl_gifts.ensembl_gene.gene_id;


--
-- Name: ensembl_species_history; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.ensembl_species_history (
    ensembl_species_history_id bigint NOT NULL,
    species character varying(30),
    assembly_accession character varying(30),
    ensembl_tax_id bigint,
    ensembl_release bigint,
    status character varying(30),
    time_loaded timestamp with time zone DEFAULT now(),
    alignment_status character varying(30)
);


ALTER TABLE ensembl_gifts.ensembl_species_history OWNER TO ensrw;

--
-- Name: ensembl_species_history_ensembl_species_history_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.ensembl_species_history_ensembl_species_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.ensembl_species_history_ensembl_species_history_id_seq OWNER TO ensrw;

--
-- Name: ensembl_species_history_ensembl_species_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.ensembl_species_history_ensembl_species_history_id_seq OWNED BY ensembl_gifts.ensembl_species_history.ensembl_species_history_id;


--
-- Name: ensembl_transcript; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.ensembl_transcript (
    transcript_id bigint NOT NULL,
    gene_id bigint,
    enst_id character varying(30),
    enst_version smallint,
    ccds_id character varying(30),
    uniparc_accession character varying(30),
    biotype character varying(40),
    deleted boolean DEFAULT false,
    seq_region_start bigint,
    seq_region_end bigint,
    supporting_evidence character varying(45),
    userstamp character varying(30),
    time_loaded timestamp with time zone,
    "select" boolean,
    ensp_id character varying(30),
    ensp_len integer,
    source character varying(30)
);


ALTER TABLE ensembl_gifts.ensembl_transcript OWNER TO ensrw;

--
-- Name: ensembl_transcript_transcript_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.ensembl_transcript_transcript_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.ensembl_transcript_transcript_id_seq OWNER TO ensrw;

--
-- Name: ensembl_transcript_transcript_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.ensembl_transcript_transcript_id_seq OWNED BY ensembl_gifts.ensembl_transcript.transcript_id;


--
-- Name: ensp_u_cigar; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.ensp_u_cigar (
    alignment_id bigint NOT NULL,
    cigarplus text,
    mdz text
);


ALTER TABLE ensembl_gifts.ensp_u_cigar OWNER TO ensrw;

--
-- Name: gene_history; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.gene_history (
    ensembl_species_history_id bigint NOT NULL,
    gene_id bigint NOT NULL
);


ALTER TABLE ensembl_gifts.gene_history OWNER TO ensrw;

--
-- Name: isoform; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.isoform (
    isoform_id bigint NOT NULL,
    uniprot_id bigint,
    accession character varying(30),
    sequence character varying(200),
    uniparc_accession character varying(30),
    embl_acc character varying(30)
);


ALTER TABLE ensembl_gifts.isoform OWNER TO ensrw;

--
-- Name: isoform_isoform_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.isoform_isoform_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.isoform_isoform_id_seq OWNER TO ensrw;

--
-- Name: isoform_isoform_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.isoform_isoform_id_seq OWNED BY ensembl_gifts.isoform.isoform_id;


--
-- Name: mapping_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.mapping_id_seq OWNER TO ensrw;

--
-- Name: mapping; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.mapping (
    mapping_id bigint DEFAULT nextval('ensembl_gifts.mapping_id_seq'::regclass) NOT NULL,
    uniprot_id bigint,
    transcript_id bigint,
    alignment_difference integer,
    status bigint DEFAULT 1,
    first_release_mapping_history_id bigint
);


ALTER TABLE ensembl_gifts.mapping OWNER TO ensrw;

--
-- Name: mapping_history_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.mapping_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.mapping_history_id_seq OWNER TO ensrw;

--
-- Name: mapping_history; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.mapping_history (
    mapping_history_id bigint DEFAULT nextval('ensembl_gifts.mapping_history_id_seq'::regclass) NOT NULL,
    release_mapping_history_id bigint NOT NULL,
    sequence_version smallint NOT NULL,
    entry_type smallint NOT NULL,
    entry_version integer NOT NULL,
    enst_version smallint NOT NULL,
    mapping_id bigint NOT NULL,
    sp_ensembl_mapping_type character varying(50),
    grouping_id bigint
);


ALTER TABLE ensembl_gifts.mapping_history OWNER TO ensrw;

--
-- Name: mapping_view; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.mapping_view (
    mapping_id bigint,
    uniprot_id bigint,
    transcript_id bigint,
    alignment_difference integer,
    status bigint,
    first_release_mapping_history_id bigint,
    uniprot_acc character varying(30),
    uniprot_tax_id bigint,
    sequence_version smallint,
    upi character(13),
    md5 character(32),
    canonical_uniprot_id integer,
    ensembl_derived boolean,
    alias character varying(30),
    entry_type smallint,
    gene_symbol_up character varying(30),
    chromosome_line character varying(50),
    length integer,
    protein_existence_id integer,
    release_version character varying(30),
    gene_id bigint,
    enst_id character varying(30),
    enst_version smallint,
    ccds_id character varying(30),
    uniparc_accession character varying(30),
    biotype character varying(40),
    deleted boolean,
    seq_region_end bigint,
    seq_region_start bigint,
    supporting_evidence character varying(45),
    "select" boolean,
    ensp_id character varying(30),
    ensp_len integer,
    source character varying(30),
    mapping_history_id bigint,
    release_mapping_history_id bigint,
    entry_version integer,
    sp_ensembl_mapping_type character varying(50),
    grouping_id bigint,
    ensg_id character varying(30),
    id bigint NOT NULL,
    chromosome character varying(50),
    region_accession character varying(50),
    gene_name character varying(255),
    gene_symbol_eg character varying(30),
    gene_accession character varying(30),
    time_mapped timestamp without time zone,
    uniprot_release character varying(7),
    ensembl_release bigint,
    seq_region_strand bigint,
    uniprot_mapping_status character varying(30),
    gene_accession_up character varying(500)
);


ALTER TABLE ensembl_gifts.mapping_view OWNER TO ensrw;

--
-- Name: mapping_view_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.mapping_view_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.mapping_view_id_seq OWNER TO ensrw;

--
-- Name: mapping_view_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.mapping_view_id_seq OWNED BY ensembl_gifts.mapping_view.id;


--
-- Name: release_mapping_history; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.release_mapping_history (
    release_mapping_history_id bigint NOT NULL,
    ensembl_species_history_id bigint,
    time_mapped timestamp without time zone DEFAULT now() NOT NULL,
    uniprot_release character varying(7),
    uniprot_taxid bigint,
    status character varying(20),
    denormalised boolean DEFAULT false
);


ALTER TABLE ensembl_gifts.release_mapping_history OWNER TO ensrw;

--
-- Name: release_mapping_history_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.release_mapping_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.release_mapping_history_id_seq OWNER TO ensrw;

--
-- Name: release_mapping_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.release_mapping_history_id_seq OWNED BY ensembl_gifts.release_mapping_history.release_mapping_history_id;


--
-- Name: release_stats; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.release_stats (
    release_mapping_history_id bigint NOT NULL,
    transcripts_total bigint,
    uniprot_entries_total bigint,
    uniprot_entries_unmapped bigint,
    genes_total bigint,
    uniprot_entries_unmapped_sp bigint,
    transcripts_unmapped bigint,
    genes_unmapped bigint,
    uniprot_entries_unmapped_isoform bigint,
    uniprot_entries_sp_total bigint,
    uniprot_entries_isoform_total bigint,
    uniprot_entries_trembl_total bigint,
    transcripts_protein_coding_total bigint,
    transcripts_protein_coding_mapped bigint,
    transcripts_protein_other_total bigint,
    transcripts_protein_other_mapped bigint,
    genes_mapped_pc bigint,
    genes_mapped_nonpc bigint,
    genes_unmapped_pc bigint,
    genes_unmapped_nonpc bigint
);


ALTER TABLE ensembl_gifts.release_stats OWNER TO ensrw;

--
-- Name: taxonomy_mapping; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.taxonomy_mapping (
    taxonomy_mapping_id bigint NOT NULL,
    ensembl_tax_id bigint,
    uniprot_tax_id bigint
);


ALTER TABLE ensembl_gifts.taxonomy_mapping OWNER TO ensrw;

--
-- Name: taxonomy_mapping_taxonomy_mapping_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.taxonomy_mapping_taxonomy_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.taxonomy_mapping_taxonomy_mapping_id_seq OWNER TO ensrw;

--
-- Name: taxonomy_mapping_taxonomy_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.taxonomy_mapping_taxonomy_mapping_id_seq OWNED BY ensembl_gifts.taxonomy_mapping.taxonomy_mapping_id;


--
-- Name: temp_isoforms; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.temp_isoforms (
    uniprot_id bigint,
    can_id bigint
);


ALTER TABLE ensembl_gifts.temp_isoforms OWNER TO ensrw;

--
-- Name: transcript_history; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.transcript_history (
    ensembl_species_history_id bigint NOT NULL,
    transcript_id bigint NOT NULL,
    grouping_id bigint
);


ALTER TABLE ensembl_gifts.transcript_history OWNER TO ensrw;

--
-- Name: ue_mapping_comment; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.ue_mapping_comment (
    id bigint NOT NULL,
    time_stamp timestamp with time zone DEFAULT now() NOT NULL,
    user_stamp character varying(50) NOT NULL,
    comment text NOT NULL,
    mapping_id bigint,
    deleted boolean DEFAULT false NOT NULL
);


ALTER TABLE ensembl_gifts.ue_mapping_comment OWNER TO ensrw;

--
-- Name: ue_mapping_comment_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.ue_mapping_comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.ue_mapping_comment_id_seq OWNER TO ensrw;

--
-- Name: ue_mapping_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.ue_mapping_comment_id_seq OWNED BY ensembl_gifts.ue_mapping_comment.id;


--
-- Name: ue_mapping_label; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.ue_mapping_label (
    id bigint NOT NULL,
    time_stamp timestamp with time zone DEFAULT now() NOT NULL,
    user_stamp character varying(50) NOT NULL,
    label bigint NOT NULL,
    mapping_id bigint NOT NULL
);


ALTER TABLE ensembl_gifts.ue_mapping_label OWNER TO ensrw;

--
-- Name: ue_mapping_label_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.ue_mapping_label_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.ue_mapping_label_id_seq OWNER TO ensrw;

--
-- Name: ue_mapping_label_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.ue_mapping_label_id_seq OWNED BY ensembl_gifts.ue_mapping_label.id;


--
-- Name: ue_mapping_status; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.ue_mapping_status (
    id bigint NOT NULL,
    time_stamp timestamp with time zone DEFAULT now() NOT NULL,
    user_stamp character varying(50),
    status bigint NOT NULL,
    mapping_id bigint NOT NULL
);


ALTER TABLE ensembl_gifts.ue_mapping_status OWNER TO ensrw;

--
-- Name: ue_mapping_status_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.ue_mapping_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.ue_mapping_status_id_seq OWNER TO ensrw;

--
-- Name: ue_mapping_status_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.ue_mapping_status_id_seq OWNED BY ensembl_gifts.ue_mapping_status.id;


--
-- Name: ue_unmapped_entry_comment; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.ue_unmapped_entry_comment (
    id bigint NOT NULL,
    time_stamp timestamp with time zone DEFAULT now() NOT NULL,
    user_stamp character varying(50) NOT NULL,
    comment text NOT NULL,
    uniprot_id bigint,
    deleted boolean DEFAULT false NOT NULL
);


ALTER TABLE ensembl_gifts.ue_unmapped_entry_comment OWNER TO ensrw;

--
-- Name: ue_unmapped_entry_comment_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.ue_unmapped_entry_comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.ue_unmapped_entry_comment_id_seq OWNER TO ensrw;

--
-- Name: ue_unmapped_entry_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.ue_unmapped_entry_comment_id_seq OWNED BY ensembl_gifts.ue_unmapped_entry_comment.id;


--
-- Name: ue_unmapped_entry_label; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.ue_unmapped_entry_label (
    id bigint NOT NULL,
    time_stamp timestamp with time zone DEFAULT now() NOT NULL,
    user_stamp character varying(50) NOT NULL,
    label bigint NOT NULL,
    uniprot_id bigint NOT NULL
);


ALTER TABLE ensembl_gifts.ue_unmapped_entry_label OWNER TO ensrw;

--
-- Name: ue_unmapped_entry_label_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.ue_unmapped_entry_label_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.ue_unmapped_entry_label_id_seq OWNER TO ensrw;

--
-- Name: ue_unmapped_entry_label_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.ue_unmapped_entry_label_id_seq OWNED BY ensembl_gifts.ue_unmapped_entry_label.id;


--
-- Name: ue_unmapped_entry_status; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.ue_unmapped_entry_status (
    id bigint NOT NULL,
    time_stamp timestamp with time zone DEFAULT now() NOT NULL,
    user_stamp character varying(50),
    status bigint NOT NULL,
    uniprot_id bigint NOT NULL
);


ALTER TABLE ensembl_gifts.ue_unmapped_entry_status OWNER TO ensrw;

--
-- Name: ue_unmapped_entry_status_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.ue_unmapped_entry_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.ue_unmapped_entry_status_id_seq OWNER TO ensrw;

--
-- Name: ue_unmapped_entry_status_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.ue_unmapped_entry_status_id_seq OWNED BY ensembl_gifts.ue_unmapped_entry_status.id;


--
-- Name: uniprot_entry; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.uniprot_entry (
    uniprot_id bigint NOT NULL,
    uniprot_acc character varying(30),
    uniprot_tax_id bigint,
    userstamp character varying(30),
    "timestamp" timestamp with time zone DEFAULT now(),
    sequence_version smallint DEFAULT '1'::smallint,
    upi character(13),
    md5 character(32),
    canonical_uniprot_id integer,
    ensembl_derived boolean,
    alias character varying(30),
    entry_type smallint,
    gene_symbol character varying(30),
    chromosome_line character varying(50),
    length integer,
    protein_existence_id integer,
    gene_accession character varying(20)
);


ALTER TABLE ensembl_gifts.uniprot_entry OWNER TO ensrw;

--
-- Name: uniprot_entry_history; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.uniprot_entry_history (
    release_version character varying(30) DEFAULT ''::character varying NOT NULL,
    uniprot_id bigint NOT NULL,
    grouping_id bigint
);


ALTER TABLE ensembl_gifts.uniprot_entry_history OWNER TO ensrw;

--
-- Name: uniprot_entry_uniprot_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.uniprot_entry_uniprot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.uniprot_entry_uniprot_id_seq OWNER TO ensrw;

--
-- Name: uniprot_entry_uniprot_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: ensrw
--

ALTER SEQUENCE ensembl_gifts.uniprot_entry_uniprot_id_seq OWNED BY ensembl_gifts.uniprot_entry.uniprot_id;


--
-- Name: uniprot_gene_accessions; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.uniprot_gene_accessions (
    uniprot_acc character varying(15) NOT NULL,
    gene_accession character varying(15) NOT NULL,
    tax_id bigint NOT NULL
);


ALTER TABLE ensembl_gifts.uniprot_gene_accessions OWNER TO ensrw;

--
-- Name: unmapped_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE SEQUENCE ensembl_gifts.unmapped_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ensembl_gifts.unmapped_seq OWNER TO ensrw;

--
-- Name: users; Type: TABLE; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TABLE ensembl_gifts.users (
    user_id integer,
    email character varying(50),
    elixir_id character varying(50),
    is_admin boolean DEFAULT false,
    validated boolean
);


ALTER TABLE ensembl_gifts.users OWNER TO ensrw;

--
-- Name: alignment alignment_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.alignment ALTER COLUMN alignment_id SET DEFAULT nextval('ensembl_gifts.alignment_alignment_id_seq'::regclass);


--
-- Name: alignment_run alignment_run_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.alignment_run ALTER COLUMN alignment_run_id SET DEFAULT nextval('ensembl_gifts.alignment_run_alignment_run_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.django_migrations ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.django_migrations_id_seq'::regclass);


--
-- Name: domain domain_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.domain ALTER COLUMN domain_id SET DEFAULT nextval('ensembl_gifts.domain_domain_id_seq'::regclass);


--
-- Name: ensembl_gene gene_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ensembl_gene ALTER COLUMN gene_id SET DEFAULT nextval('ensembl_gifts.ensembl_gene_gene_id_seq'::regclass);


--
-- Name: ensembl_species_history ensembl_species_history_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ensembl_species_history ALTER COLUMN ensembl_species_history_id SET DEFAULT nextval('ensembl_gifts.ensembl_species_history_ensembl_species_history_id_seq'::regclass);


--
-- Name: ensembl_transcript transcript_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ensembl_transcript ALTER COLUMN transcript_id SET DEFAULT nextval('ensembl_gifts.ensembl_transcript_transcript_id_seq'::regclass);


--
-- Name: isoform isoform_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.isoform ALTER COLUMN isoform_id SET DEFAULT nextval('ensembl_gifts.isoform_isoform_id_seq'::regclass);


--
-- Name: mapping_view id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.mapping_view ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.mapping_view_id_seq'::regclass);


--
-- Name: release_mapping_history release_mapping_history_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.release_mapping_history ALTER COLUMN release_mapping_history_id SET DEFAULT nextval('ensembl_gifts.release_mapping_history_id_seq'::regclass);


--
-- Name: taxonomy_mapping taxonomy_mapping_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.taxonomy_mapping ALTER COLUMN taxonomy_mapping_id SET DEFAULT nextval('ensembl_gifts.taxonomy_mapping_taxonomy_mapping_id_seq'::regclass);


--
-- Name: ue_mapping_comment id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_comment ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.ue_mapping_comment_id_seq'::regclass);


--
-- Name: ue_mapping_label id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_label ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.ue_mapping_label_id_seq'::regclass);


--
-- Name: ue_mapping_status id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_status ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.ue_mapping_status_id_seq'::regclass);


--
-- Name: ue_unmapped_entry_comment id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_unmapped_entry_comment ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.ue_unmapped_entry_comment_id_seq'::regclass);


--
-- Name: ue_unmapped_entry_label id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_unmapped_entry_label ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.ue_unmapped_entry_label_id_seq'::regclass);


--
-- Name: ue_unmapped_entry_status id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_unmapped_entry_status ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.ue_unmapped_entry_status_id_seq'::regclass);


--
-- Name: uniprot_entry uniprot_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry ALTER COLUMN uniprot_id SET DEFAULT nextval('ensembl_gifts.uniprot_entry_uniprot_id_seq'::regclass);


--
-- Name: aap_auth_aapuser aap_auth_aapuser_pkey; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.aap_auth_aapuser
    ADD CONSTRAINT aap_auth_aapuser_pkey PRIMARY KEY (elixir_id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: mapping ensembl_uniprot_pk; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.mapping
    ADD CONSTRAINT ensembl_uniprot_pk PRIMARY KEY (mapping_id);


--
-- Name: alignment idx_24996_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.alignment
    ADD CONSTRAINT idx_24996_primary PRIMARY KEY (alignment_id);


--
-- Name: alignment_run idx_25002_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.alignment_run
    ADD CONSTRAINT idx_25002_primary PRIMARY KEY (alignment_run_id);


--
-- Name: cv_entry_type idx_25010_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.cv_entry_type
    ADD CONSTRAINT idx_25010_primary PRIMARY KEY (id);


--
-- Name: cv_ue_label idx_25014_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.cv_ue_label
    ADD CONSTRAINT idx_25014_primary PRIMARY KEY (id);


--
-- Name: cv_ue_status idx_25017_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.cv_ue_status
    ADD CONSTRAINT idx_25017_primary PRIMARY KEY (id);


--
-- Name: domain idx_25022_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.domain
    ADD CONSTRAINT idx_25022_primary PRIMARY KEY (domain_id);


--
-- Name: ensembl_gene idx_25028_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ensembl_gene
    ADD CONSTRAINT idx_25028_primary PRIMARY KEY (gene_id);


--
-- Name: ensembl_species_history idx_25036_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ensembl_species_history
    ADD CONSTRAINT idx_25036_primary PRIMARY KEY (ensembl_species_history_id);


--
-- Name: ensembl_transcript idx_25043_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ensembl_transcript
    ADD CONSTRAINT idx_25043_primary PRIMARY KEY (transcript_id);


--
-- Name: gene_history idx_25064_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.gene_history
    ADD CONSTRAINT idx_25064_primary PRIMARY KEY (ensembl_species_history_id, gene_id);


--
-- Name: isoform idx_25075_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.isoform
    ADD CONSTRAINT idx_25075_primary PRIMARY KEY (isoform_id);


--
-- Name: release_mapping_history idx_25081_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.release_mapping_history
    ADD CONSTRAINT idx_25081_primary PRIMARY KEY (release_mapping_history_id);


--
-- Name: taxonomy_mapping idx_25100_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.taxonomy_mapping
    ADD CONSTRAINT idx_25100_primary PRIMARY KEY (taxonomy_mapping_id);


--
-- Name: ue_mapping_comment idx_25111_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_comment
    ADD CONSTRAINT idx_25111_primary PRIMARY KEY (id);


--
-- Name: ue_mapping_label idx_25121_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_label
    ADD CONSTRAINT idx_25121_primary PRIMARY KEY (id);


--
-- Name: ue_mapping_status idx_25128_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_status
    ADD CONSTRAINT idx_25128_primary PRIMARY KEY (id);


--
-- Name: mapping_history mapping_history_pk; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.mapping_history
    ADD CONSTRAINT mapping_history_pk PRIMARY KEY (mapping_history_id);


--
-- Name: mapping_view mapping_view_pk; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.mapping_view
    ADD CONSTRAINT mapping_view_pk PRIMARY KEY (id);


--
-- Name: release_stats release_stats_pk; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.release_stats
    ADD CONSTRAINT release_stats_pk PRIMARY KEY (release_mapping_history_id);


--
-- Name: transcript_history transcript_history_pkey; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.transcript_history
    ADD CONSTRAINT transcript_history_pkey PRIMARY KEY (ensembl_species_history_id, transcript_id);


--
-- Name: ue_unmapped_entry_comment ue_unmapped_entry_comment_pk; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_unmapped_entry_comment
    ADD CONSTRAINT ue_unmapped_entry_comment_pk PRIMARY KEY (id);


--
-- Name: ue_unmapped_entry_label ue_unmapped_entry_label_pk; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_unmapped_entry_label
    ADD CONSTRAINT ue_unmapped_entry_label_pk PRIMARY KEY (id);


--
-- Name: ue_unmapped_entry_status ue_unmapped_entry_status_pk; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_unmapped_entry_status
    ADD CONSTRAINT ue_unmapped_entry_status_pk PRIMARY KEY (id);


--
-- Name: uniprot_entry_history uniprot_entry_history_pk; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry_history
    ADD CONSTRAINT uniprot_entry_history_pk PRIMARY KEY (uniprot_id, release_version);


--
-- Name: uniprot_entry uniprot_entry_pk; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry
    ADD CONSTRAINT uniprot_entry_pk PRIMARY KEY (uniprot_id);


--
-- Name: uniprot_gene_accessions uniprot_gene_accessions_pk; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.uniprot_gene_accessions
    ADD CONSTRAINT uniprot_gene_accessions_pk PRIMARY KEY (gene_accession, uniprot_acc);


--
-- Name: ensembl_gifts_test100.aap_auth_aapuser_elixir_id_1626a210_like; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX "ensembl_gifts_test100.aap_auth_aapuser_elixir_id_1626a210_like" ON ensembl_gifts.aap_auth_aapuser USING btree (elixir_id varchar_pattern_ops);


--
-- Name: idx_24996_alignment_run_id; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_24996_alignment_run_id ON ensembl_gifts.alignment USING btree (alignment_run_id);


--
-- Name: idx_24996_transcript_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_24996_transcript_id_idx ON ensembl_gifts.alignment USING btree (transcript_id);


--
-- Name: idx_24996_uniprot_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_24996_uniprot_id_idx ON ensembl_gifts.alignment USING btree (uniprot_id);


--
-- Name: idx_25002_mapping_history_id; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_25002_mapping_history_id ON ensembl_gifts.alignment_run USING btree (release_mapping_history_id);


--
-- Name: idx_25022_isoform_id; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_25022_isoform_id ON ensembl_gifts.domain USING btree (isoform_id);


--
-- Name: idx_25043_enst_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE UNIQUE INDEX idx_25043_enst_id_idx ON ensembl_gifts.ensembl_transcript USING btree (enst_id);


--
-- Name: idx_25043_gene_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_25043_gene_id_idx ON ensembl_gifts.ensembl_transcript USING btree (gene_id);


--
-- Name: idx_25064_gh_g_id; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_25064_gh_g_id ON ensembl_gifts.gene_history USING btree (gene_id);


--
-- Name: idx_25075_uniform_isoform_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_25075_uniform_isoform_idx ON ensembl_gifts.isoform USING btree (uniprot_id);


--
-- Name: idx_alignment_difference; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_alignment_difference ON ensembl_gifts.mapping USING btree (alignment_difference);


--
-- Name: idx_stable_id_gene; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE UNIQUE INDEX idx_stable_id_gene ON ensembl_gifts.ensembl_gene USING btree (ensg_id);


--
-- Name: idx_transcript_id; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_transcript_id ON ensembl_gifts.mapping USING btree (transcript_id);


--
-- Name: idx_transcripthistory_transcriptid; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_transcripthistory_transcriptid ON ensembl_gifts.transcript_history USING btree (transcript_id);


--
-- Name: idx_uemappingstatus_mapping_id; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX idx_uemappingstatus_mapping_id ON ensembl_gifts.ue_mapping_status USING btree (mapping_id);


--
-- Name: mapping_history_mapping_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_history_mapping_id_idx ON ensembl_gifts.mapping_history USING btree (mapping_id);


--
-- Name: mapping_history_release_mapping_history_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_history_release_mapping_history_id_idx ON ensembl_gifts.mapping_history USING btree (release_mapping_history_id);


--
-- Name: mapping_uniprot_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_uniprot_id_idx ON ensembl_gifts.mapping USING btree (uniprot_id);


--
-- Name: mapping_view_ensg_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_view_ensg_id_idx ON ensembl_gifts.mapping_view USING btree (ensg_id);


--
-- Name: mapping_view_enst_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_view_enst_id_idx ON ensembl_gifts.mapping_view USING btree (enst_id);


--
-- Name: mapping_view_grouping_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_view_grouping_id_idx ON ensembl_gifts.mapping_view USING btree (grouping_id);


--
-- Name: mapping_view_mapping_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_view_mapping_id_idx ON ensembl_gifts.mapping_view USING btree (mapping_id);


--
-- Name: mapping_view_release_mapping_history_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_view_release_mapping_history_id_idx ON ensembl_gifts.mapping_view USING btree (release_mapping_history_id, grouping_id);


--
-- Name: mapping_view_uniprot_acc_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_view_uniprot_acc_idx ON ensembl_gifts.mapping_view USING btree (uniprot_acc);


--
-- Name: mapping_view_uniprot_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_view_uniprot_id_idx ON ensembl_gifts.mapping_view USING btree (uniprot_id);


--
-- Name: mapping_view_uniprot_mapping_status_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_view_uniprot_mapping_status_idx ON ensembl_gifts.mapping_view USING btree (uniprot_mapping_status);


--
-- Name: mapping_view_uniprot_tax_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX mapping_view_uniprot_tax_id_idx ON ensembl_gifts.mapping_view USING btree (uniprot_tax_id);


--
-- Name: ue_mapping_comment_mapping_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX ue_mapping_comment_mapping_id_idx ON ensembl_gifts.ue_mapping_comment USING btree (mapping_id);


--
-- Name: ue_mapping_label_mapping_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX ue_mapping_label_mapping_id_idx ON ensembl_gifts.ue_mapping_label USING btree (mapping_id);


--
-- Name: ue_unmapped_entry_comment_uniprot_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX ue_unmapped_entry_comment_uniprot_id_idx ON ensembl_gifts.ue_unmapped_entry_comment USING btree (uniprot_id);


--
-- Name: ue_unmapped_entry_label_uniprot_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX ue_unmapped_entry_label_uniprot_id_idx ON ensembl_gifts.ue_unmapped_entry_label USING btree (uniprot_id);


--
-- Name: ue_unmapped_entry_status_uniprot_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX ue_unmapped_entry_status_uniprot_id_idx ON ensembl_gifts.ue_unmapped_entry_status USING btree (uniprot_id);


--
-- Name: uniprot_entry_uniprot_acc_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE UNIQUE INDEX uniprot_entry_uniprot_acc_idx ON ensembl_gifts.uniprot_entry USING btree (uniprot_acc, sequence_version);


--
-- Name: uniprot_gene_accessions_tax_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: ensrw
--

CREATE INDEX uniprot_gene_accessions_tax_id_idx ON ensembl_gifts.uniprot_gene_accessions USING btree (tax_id);


--
-- Name: mapping default_mapping_status; Type: TRIGGER; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TRIGGER default_mapping_status AFTER INSERT ON ensembl_gifts.mapping FOR EACH ROW EXECUTE PROCEDURE ensembl_gifts.on_mapping_insert_add_default_status();


--
-- Name: release_mapping_history on_update_current_timestamp; Type: TRIGGER; Schema: ensembl_gifts; Owner: ensrw
--

CREATE TRIGGER on_update_current_timestamp BEFORE UPDATE ON ensembl_gifts.release_mapping_history FOR EACH ROW EXECUTE PROCEDURE ensembl_gifts.on_update_current_timestamp_mapping_history();


--
-- Name: alignment alignment_alignment_run_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.alignment
    ADD CONSTRAINT alignment_alignment_run_fk FOREIGN KEY (alignment_run_id) REFERENCES ensembl_gifts.alignment_run(alignment_run_id) ON DELETE CASCADE;


--
-- Name: alignment alignment_ensembl_uniprot_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.alignment
    ADD CONSTRAINT alignment_ensembl_uniprot_fk FOREIGN KEY (mapping_id) REFERENCES ensembl_gifts.mapping(mapping_id);


--
-- Name: mapping ensembl_uniprot_ensembl_transcript_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.mapping
    ADD CONSTRAINT ensembl_uniprot_ensembl_transcript_fk FOREIGN KEY (transcript_id) REFERENCES ensembl_gifts.ensembl_transcript(transcript_id);


--
-- Name: mapping ensembl_uniprot_uniprot_entry_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.mapping
    ADD CONSTRAINT ensembl_uniprot_uniprot_entry_fk FOREIGN KEY (uniprot_id) REFERENCES ensembl_gifts.uniprot_entry(uniprot_id);


--
-- Name: ensp_u_cigar ensp_u_cigar_alignment_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ensp_u_cigar
    ADD CONSTRAINT ensp_u_cigar_alignment_fk FOREIGN KEY (alignment_id) REFERENCES ensembl_gifts.alignment(alignment_id) ON DELETE CASCADE;


--
-- Name: ensembl_transcript g_id; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ensembl_transcript
    ADD CONSTRAINT g_id FOREIGN KEY (gene_id) REFERENCES ensembl_gifts.ensembl_gene(gene_id);


--
-- Name: gene_history gh_g_id; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.gene_history
    ADD CONSTRAINT gh_g_id FOREIGN KEY (gene_id) REFERENCES ensembl_gifts.ensembl_gene(gene_id);


--
-- Name: gene_history gh_h_id; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.gene_history
    ADD CONSTRAINT gh_h_id FOREIGN KEY (ensembl_species_history_id) REFERENCES ensembl_gifts.ensembl_species_history(ensembl_species_history_id);


--
-- Name: domain isoform_idx; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.domain
    ADD CONSTRAINT isoform_idx FOREIGN KEY (isoform_id) REFERENCES ensembl_gifts.isoform(isoform_id);


--
-- Name: mapping_history mapping_history_mapping_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.mapping_history
    ADD CONSTRAINT mapping_history_mapping_fk FOREIGN KEY (mapping_id) REFERENCES ensembl_gifts.mapping(mapping_id) ON DELETE CASCADE;


--
-- Name: mapping_history mapping_history_release_mapping_history_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.mapping_history
    ADD CONSTRAINT mapping_history_release_mapping_history_fk FOREIGN KEY (release_mapping_history_id) REFERENCES ensembl_gifts.release_mapping_history(release_mapping_history_id) ON DELETE CASCADE;


--
-- Name: release_mapping_history release_mapping_history_ensembl_species_history_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.release_mapping_history
    ADD CONSTRAINT release_mapping_history_ensembl_species_history_fk FOREIGN KEY (ensembl_species_history_id) REFERENCES ensembl_gifts.ensembl_species_history(ensembl_species_history_id);


--
-- Name: release_stats release_stats_release_mapping_history_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.release_stats
    ADD CONSTRAINT release_stats_release_mapping_history_fk FOREIGN KEY (release_mapping_history_id) REFERENCES ensembl_gifts.release_mapping_history(release_mapping_history_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: transcript_history transcript_history_ensembl_species_history_id_fkey; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.transcript_history
    ADD CONSTRAINT transcript_history_ensembl_species_history_id_fkey FOREIGN KEY (ensembl_species_history_id) REFERENCES ensembl_gifts.ensembl_species_history(ensembl_species_history_id);


--
-- Name: transcript_history transcript_history_transcript_id_fkey; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.transcript_history
    ADD CONSTRAINT transcript_history_transcript_id_fkey FOREIGN KEY (transcript_id) REFERENCES ensembl_gifts.ensembl_transcript(transcript_id);


--
-- Name: alignment transcript_id_idx; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.alignment
    ADD CONSTRAINT transcript_id_idx FOREIGN KEY (transcript_id) REFERENCES ensembl_gifts.ensembl_transcript(transcript_id);


--
-- Name: ue_mapping_comment ue_mapping_comment_ensembl_uniprot_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_comment
    ADD CONSTRAINT ue_mapping_comment_ensembl_uniprot_fk FOREIGN KEY (mapping_id) REFERENCES ensembl_gifts.mapping(mapping_id);


--
-- Name: ue_mapping_label ue_mapping_label_ensembl_uniprot_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_label
    ADD CONSTRAINT ue_mapping_label_ensembl_uniprot_fk FOREIGN KEY (mapping_id) REFERENCES ensembl_gifts.mapping(mapping_id);


--
-- Name: ue_mapping_status ue_mapping_status_ensembl_uniprot_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_status
    ADD CONSTRAINT ue_mapping_status_ensembl_uniprot_fk FOREIGN KEY (mapping_id) REFERENCES ensembl_gifts.mapping(mapping_id);


--
-- Name: ue_unmapped_entry_comment ue_unmapped_entry_comment_uniprot_entry_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_unmapped_entry_comment
    ADD CONSTRAINT ue_unmapped_entry_comment_uniprot_entry_fk FOREIGN KEY (uniprot_id) REFERENCES ensembl_gifts.uniprot_entry(uniprot_id);


--
-- Name: ue_unmapped_entry_label ue_unmapped_entry_label_uniprot_entry_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_unmapped_entry_label
    ADD CONSTRAINT ue_unmapped_entry_label_uniprot_entry_fk FOREIGN KEY (uniprot_id) REFERENCES ensembl_gifts.uniprot_entry(uniprot_id);


--
-- Name: ue_unmapped_entry_status ue_unmapped_entry_status_uniprot_entry_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.ue_unmapped_entry_status
    ADD CONSTRAINT ue_unmapped_entry_status_uniprot_entry_fk FOREIGN KEY (uniprot_id) REFERENCES ensembl_gifts.uniprot_entry(uniprot_id);


--
-- Name: uniprot_entry uniprot_entry_cv_entry_type_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry
    ADD CONSTRAINT uniprot_entry_cv_entry_type_fk FOREIGN KEY (entry_type) REFERENCES ensembl_gifts.cv_entry_type(id);


--
-- Name: uniprot_entry_history uniprot_entry_history_uniprot_entry_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: ensrw
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry_history
    ADD CONSTRAINT uniprot_entry_history_uniprot_entry_fk FOREIGN KEY (uniprot_id) REFERENCES ensembl_gifts.uniprot_entry(uniprot_id);


--
-- PostgreSQL database dump complete
--

