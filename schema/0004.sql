--
-- PostgreSQL database dump
--

-- Dumped from database version 10.4 (Ubuntu 10.4-1.pgdg16.04+1)
-- Dumped by pg_dump version 10.4 (Ubuntu 10.4-1.pgdg16.04+1)

-- Started on 2018-05-24 11:33:55 BST

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
-- TOC entry 9 (class 2615 OID 19682)
-- Name: ensembl_gifts; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA ensembl_gifts;


--
-- TOC entry 243 (class 1255 OID 19684)
-- Name: on_update_current_timestamp_mapping_history(); Type: FUNCTION; Schema: ensembl_gifts; Owner: -
--

CREATE FUNCTION ensembl_gifts.on_update_current_timestamp_mapping_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   NEW.time_mapped = now();
   RETURN NEW;
END;
$$;


SET default_with_oids = false;

--
-- TOC entry 198 (class 1259 OID 19685)
-- Name: alignment; Type: TABLE; Schema: ensembl_gifts; Owner: -
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


--
-- TOC entry 199 (class 1259 OID 19688)
-- Name: alignment_alignment_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.alignment_alignment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3122 (class 0 OID 0)
-- Dependencies: 199
-- Name: alignment_alignment_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.alignment_alignment_id_seq OWNED BY ensembl_gifts.alignment.alignment_id;


--
-- TOC entry 200 (class 1259 OID 19690)
-- Name: alignment_run; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.alignment_run (
    alignment_run_id bigint NOT NULL,
    userstamp character varying(30),
    time_run timestamp with time zone DEFAULT now(),
    score1_type character varying(30),
    report_type character varying(30),
    pipeline_name character varying(30) NOT NULL,
    pipeline_comment character varying(300) NOT NULL,
    mapping_history_id bigint NOT NULL,
    ensembl_release bigint NOT NULL,
    uniprot_file_swissprot character varying(300),
    uniprot_file_isoform character varying(300),
    uniprot_dir_trembl character varying(300),
    logfile_dir character varying(300),
    pipeline_script character varying(300) NOT NULL,
    score2_type character varying(30)
);


--
-- TOC entry 201 (class 1259 OID 19697)
-- Name: alignment_run_alignment_run_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.alignment_run_alignment_run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3123 (class 0 OID 0)
-- Dependencies: 201
-- Name: alignment_run_alignment_run_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.alignment_run_alignment_run_id_seq OWNED BY ensembl_gifts.alignment_run.alignment_run_id;


--
-- TOC entry 202 (class 1259 OID 19699)
-- Name: cv_entry_type; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.cv_entry_type (
    id bigint DEFAULT '0'::bigint NOT NULL,
    description character varying(20)
);


--
-- TOC entry 203 (class 1259 OID 19703)
-- Name: cv_ue_label; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.cv_ue_label (
    id bigint NOT NULL,
    description character varying(20) NOT NULL
);


--
-- TOC entry 204 (class 1259 OID 19706)
-- Name: cv_ue_status; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.cv_ue_status (
    id bigint NOT NULL,
    description character varying(20) NOT NULL
);


--
-- TOC entry 205 (class 1259 OID 19709)
-- Name: domain; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.domain (
    domain_id bigint NOT NULL,
    isoform_id bigint,
    start bigint,
    "end" bigint,
    description character varying(45)
);


--
-- TOC entry 206 (class 1259 OID 19712)
-- Name: domain_domain_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.domain_domain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3124 (class 0 OID 0)
-- Dependencies: 206
-- Name: domain_domain_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.domain_domain_id_seq OWNED BY ensembl_gifts.domain.domain_id;


--
-- TOC entry 207 (class 1259 OID 19714)
-- Name: ensembl_gene; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.ensembl_gene (
    gene_id bigint NOT NULL,
    ensg_id character varying(30),
    gene_name character varying(30),
    chromosome character varying(50),
    region_accession character varying(50),
    mod_id character varying(30),
    deleted boolean DEFAULT false,
    seq_region_start bigint,
    seq_region_end bigint,
    seq_region_strand bigint DEFAULT '1'::bigint,
    biotype character varying(40),
    time_loaded timestamp with time zone
);


--
-- TOC entry 208 (class 1259 OID 19719)
-- Name: ensembl_gene_gene_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.ensembl_gene_gene_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3125 (class 0 OID 0)
-- Dependencies: 208
-- Name: ensembl_gene_gene_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.ensembl_gene_gene_id_seq OWNED BY ensembl_gifts.ensembl_gene.gene_id;


--
-- TOC entry 209 (class 1259 OID 19721)
-- Name: ensembl_species_history; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.ensembl_species_history (
    ensembl_species_history_id bigint NOT NULL,
    species character varying(30),
    assembly_accession character varying(30),
    ensembl_tax_id bigint,
    ensembl_release bigint,
    status character varying(30),
    time_loaded timestamp with time zone DEFAULT now()
);


--
-- TOC entry 210 (class 1259 OID 19725)
-- Name: ensembl_species_history_ensembl_species_history_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.ensembl_species_history_ensembl_species_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3126 (class 0 OID 0)
-- Dependencies: 210
-- Name: ensembl_species_history_ensembl_species_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.ensembl_species_history_ensembl_species_history_id_seq OWNED BY ensembl_gifts.ensembl_species_history.ensembl_species_history_id;


--
-- TOC entry 211 (class 1259 OID 19727)
-- Name: ensembl_transcript; Type: TABLE; Schema: ensembl_gifts; Owner: -
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
    time_loaded timestamp with time zone
);


--
-- TOC entry 212 (class 1259 OID 19731)
-- Name: ensembl_transcript_transcript_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.ensembl_transcript_transcript_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3127 (class 0 OID 0)
-- Dependencies: 212
-- Name: ensembl_transcript_transcript_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.ensembl_transcript_transcript_id_seq OWNED BY ensembl_gifts.ensembl_transcript.transcript_id;


--
-- TOC entry 213 (class 1259 OID 19733)
-- Name: ensembl_uniprot; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.ensembl_uniprot (
    mapping_id bigint NOT NULL,
    uniprot_id bigint,
    userstamp character varying(30),
    "timestamp" timestamp with time zone DEFAULT now(),
    mapping_history_id bigint,
    transcript_id bigint,
    sp_ensembl_mapping_type character varying(50),
    uniprot_entry_version integer,
    uniprot_ensembl_derived smallint,
    grouping_id bigint
);


--
-- TOC entry 214 (class 1259 OID 19737)
-- Name: ensembl_uniprot_mapping_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.ensembl_uniprot_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3128 (class 0 OID 0)
-- Dependencies: 214
-- Name: ensembl_uniprot_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.ensembl_uniprot_mapping_id_seq OWNED BY ensembl_gifts.ensembl_uniprot.mapping_id;


--
-- TOC entry 215 (class 1259 OID 19739)
-- Name: ensp_u_cigar; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.ensp_u_cigar (
    ensp_u_cigar_id bigint NOT NULL,
    cigarplus text,
    mdz text,
    uniprot_acc character varying(30) NOT NULL,
    uniprot_seq_version smallint NOT NULL,
    ensp_id character varying(30) NOT NULL
);


--
-- TOC entry 216 (class 1259 OID 19745)
-- Name: ensp_u_cigar_ensp_u_cigar_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.ensp_u_cigar_ensp_u_cigar_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3129 (class 0 OID 0)
-- Dependencies: 216
-- Name: ensp_u_cigar_ensp_u_cigar_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.ensp_u_cigar_ensp_u_cigar_id_seq OWNED BY ensembl_gifts.ensp_u_cigar.ensp_u_cigar_id;


--
-- TOC entry 217 (class 1259 OID 19747)
-- Name: gene_history; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.gene_history (
    ensembl_species_history_id bigint NOT NULL,
    gene_id bigint NOT NULL
);


--
-- TOC entry 218 (class 1259 OID 19750)
-- Name: isoform; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.isoform (
    isoform_id bigint NOT NULL,
    uniprot_id bigint,
    accession character varying(30),
    sequence character varying(200),
    uniparc_accession character varying(30),
    embl_acc character varying(30)
);


--
-- TOC entry 219 (class 1259 OID 19753)
-- Name: isoform_isoform_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.isoform_isoform_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3130 (class 0 OID 0)
-- Dependencies: 219
-- Name: isoform_isoform_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.isoform_isoform_id_seq OWNED BY ensembl_gifts.isoform.isoform_id;


--
-- TOC entry 220 (class 1259 OID 19755)
-- Name: mapping_history; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.mapping_history (
    mapping_history_id bigint NOT NULL,
    ensembl_species_history_id bigint,
    time_mapped timestamp without time zone DEFAULT now() NOT NULL,
    entries_mapped bigint,
    entries_unmapped bigint,
    uniprot_release character varying(7),
    uniprot_taxid bigint,
    status character varying(20)
);


--
-- TOC entry 221 (class 1259 OID 19759)
-- Name: mapping_history_mapping_history_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.mapping_history_mapping_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3131 (class 0 OID 0)
-- Dependencies: 221
-- Name: mapping_history_mapping_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.mapping_history_mapping_history_id_seq OWNED BY ensembl_gifts.mapping_history.mapping_history_id;


--
-- TOC entry 222 (class 1259 OID 19761)
-- Name: pdb_ens; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.pdb_ens (
    pdb_ens_id bigint NOT NULL,
    pdb_acc character varying(45) NOT NULL,
    pdb_release character varying(11) NOT NULL,
    uniprot_acc character varying(30) NOT NULL,
    enst_id character varying(30) NOT NULL,
    enst_version bigint,
    ensp_id character varying(30) NOT NULL,
    ensp_start bigint,
    ensp_end bigint,
    pdb_start bigint,
    pdb_end bigint,
    pdb_chain character varying(6) NOT NULL
);


--
-- TOC entry 223 (class 1259 OID 19764)
-- Name: pdb_ens_pdb_ens_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.pdb_ens_pdb_ens_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3132 (class 0 OID 0)
-- Dependencies: 223
-- Name: pdb_ens_pdb_ens_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.pdb_ens_pdb_ens_id_seq OWNED BY ensembl_gifts.pdb_ens.pdb_ens_id;


--
-- TOC entry 224 (class 1259 OID 19766)
-- Name: ptm; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.ptm (
    ptm_id bigint NOT NULL,
    domain_id bigint,
    description character varying(45),
    start bigint,
    "end" bigint
);


--
-- TOC entry 225 (class 1259 OID 19769)
-- Name: ptm_ptm_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.ptm_ptm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3133 (class 0 OID 0)
-- Dependencies: 225
-- Name: ptm_ptm_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.ptm_ptm_id_seq OWNED BY ensembl_gifts.ptm.ptm_id;


--
-- TOC entry 226 (class 1259 OID 19771)
-- Name: taxonomy_mapping; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.taxonomy_mapping (
    taxonomy_mapping_id bigint NOT NULL,
    ensembl_tax_id bigint,
    uniprot_tax_id bigint
);


--
-- TOC entry 227 (class 1259 OID 19774)
-- Name: taxonomy_mapping_taxonomy_mapping_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.taxonomy_mapping_taxonomy_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3134 (class 0 OID 0)
-- Dependencies: 227
-- Name: taxonomy_mapping_taxonomy_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.taxonomy_mapping_taxonomy_mapping_id_seq OWNED BY ensembl_gifts.taxonomy_mapping.taxonomy_mapping_id;


--
-- TOC entry 228 (class 1259 OID 19776)
-- Name: temp_map; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.temp_map (
    uniprot_id bigint DEFAULT '0'::bigint NOT NULL,
    uniprot_entry_version_id bigint DEFAULT '0'::bigint NOT NULL
);


--
-- TOC entry 241 (class 1259 OID 20099)
-- Name: transcript_history; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.transcript_history (
    ensembl_species_history_id bigint NOT NULL,
    transcript_id bigint NOT NULL
);


--
-- TOC entry 229 (class 1259 OID 19781)
-- Name: ue_mapping_comment; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.ue_mapping_comment (
    id bigint NOT NULL,
    uniprot_acc character varying(30) NOT NULL,
    enst_id character varying(30) NOT NULL,
    time_stamp timestamp with time zone DEFAULT now() NOT NULL,
    user_stamp character varying(20) NOT NULL,
    comment text NOT NULL
);


--
-- TOC entry 230 (class 1259 OID 19788)
-- Name: ue_mapping_comment_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.ue_mapping_comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3135 (class 0 OID 0)
-- Dependencies: 230
-- Name: ue_mapping_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.ue_mapping_comment_id_seq OWNED BY ensembl_gifts.ue_mapping_comment.id;


--
-- TOC entry 231 (class 1259 OID 19790)
-- Name: ue_mapping_label; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.ue_mapping_label (
    id bigint NOT NULL,
    uniprot_acc character varying(30) NOT NULL,
    enst_id character varying(30) NOT NULL,
    time_stamp timestamp with time zone DEFAULT now() NOT NULL,
    user_stamp character varying(20) NOT NULL,
    label bigint NOT NULL
);


--
-- TOC entry 232 (class 1259 OID 19794)
-- Name: ue_mapping_label_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.ue_mapping_label_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3136 (class 0 OID 0)
-- Dependencies: 232
-- Name: ue_mapping_label_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.ue_mapping_label_id_seq OWNED BY ensembl_gifts.ue_mapping_label.id;


--
-- TOC entry 233 (class 1259 OID 19796)
-- Name: ue_mapping_status; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.ue_mapping_status (
    id bigint NOT NULL,
    uniprot_acc character varying(30) NOT NULL,
    enst_id character varying(30) NOT NULL,
    time_stamp timestamp with time zone DEFAULT now() NOT NULL,
    user_stamp character varying(20) NOT NULL,
    status bigint NOT NULL
);


--
-- TOC entry 234 (class 1259 OID 19800)
-- Name: ue_mapping_status_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.ue_mapping_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3137 (class 0 OID 0)
-- Dependencies: 234
-- Name: ue_mapping_status_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.ue_mapping_status_id_seq OWNED BY ensembl_gifts.ue_mapping_status.id;


--
-- TOC entry 235 (class 1259 OID 19802)
-- Name: uniprot_entry; Type: TABLE; Schema: ensembl_gifts; Owner: -
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
    ensembl_derived boolean
);


--
-- TOC entry 236 (class 1259 OID 19807)
-- Name: uniprot_entry_history; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.uniprot_entry_history (
    uniprot_entry_type_id bigint NOT NULL,
    release_version character varying(30) DEFAULT ''::character varying NOT NULL
);


--
-- TOC entry 237 (class 1259 OID 19811)
-- Name: uniprot_entry_history_uniprot_entry_type_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.uniprot_entry_history_uniprot_entry_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3138 (class 0 OID 0)
-- Dependencies: 237
-- Name: uniprot_entry_history_uniprot_entry_type_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.uniprot_entry_history_uniprot_entry_type_id_seq OWNED BY ensembl_gifts.uniprot_entry_history.uniprot_entry_type_id;


--
-- TOC entry 238 (class 1259 OID 19813)
-- Name: uniprot_entry_type; Type: TABLE; Schema: ensembl_gifts; Owner: -
--

CREATE TABLE ensembl_gifts.uniprot_entry_type (
    uniprot_entry_type_id bigint NOT NULL,
    userstamp character varying(30),
    "timestamp" timestamp with time zone DEFAULT now(),
    uniprot_id bigint,
    entry_type boolean
);


--
-- TOC entry 240 (class 1259 OID 19819)
-- Name: uniprot_entry_type_uniprot_entry_type_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.uniprot_entry_type_uniprot_entry_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3139 (class 0 OID 0)
-- Dependencies: 240
-- Name: uniprot_entry_type_uniprot_entry_type_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.uniprot_entry_type_uniprot_entry_type_id_seq OWNED BY ensembl_gifts.uniprot_entry_type.uniprot_entry_type_id;


--
-- TOC entry 239 (class 1259 OID 19817)
-- Name: uniprot_entry_uniprot_id_seq; Type: SEQUENCE; Schema: ensembl_gifts; Owner: -
--

CREATE SEQUENCE ensembl_gifts.uniprot_entry_uniprot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3140 (class 0 OID 0)
-- Dependencies: 239
-- Name: uniprot_entry_uniprot_id_seq; Type: SEQUENCE OWNED BY; Schema: ensembl_gifts; Owner: -
--

ALTER SEQUENCE ensembl_gifts.uniprot_entry_uniprot_id_seq OWNED BY ensembl_gifts.uniprot_entry.uniprot_id;


--
-- TOC entry 2881 (class 2604 OID 19821)
-- Name: alignment alignment_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.alignment ALTER COLUMN alignment_id SET DEFAULT nextval('ensembl_gifts.alignment_alignment_id_seq'::regclass);


--
-- TOC entry 2883 (class 2604 OID 19822)
-- Name: alignment_run alignment_run_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.alignment_run ALTER COLUMN alignment_run_id SET DEFAULT nextval('ensembl_gifts.alignment_run_alignment_run_id_seq'::regclass);


--
-- TOC entry 2885 (class 2604 OID 19823)
-- Name: domain domain_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.domain ALTER COLUMN domain_id SET DEFAULT nextval('ensembl_gifts.domain_domain_id_seq'::regclass);


--
-- TOC entry 2888 (class 2604 OID 19824)
-- Name: ensembl_gene gene_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_gene ALTER COLUMN gene_id SET DEFAULT nextval('ensembl_gifts.ensembl_gene_gene_id_seq'::regclass);


--
-- TOC entry 2890 (class 2604 OID 19825)
-- Name: ensembl_species_history ensembl_species_history_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_species_history ALTER COLUMN ensembl_species_history_id SET DEFAULT nextval('ensembl_gifts.ensembl_species_history_ensembl_species_history_id_seq'::regclass);


--
-- TOC entry 2892 (class 2604 OID 19826)
-- Name: ensembl_transcript transcript_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_transcript ALTER COLUMN transcript_id SET DEFAULT nextval('ensembl_gifts.ensembl_transcript_transcript_id_seq'::regclass);


--
-- TOC entry 2894 (class 2604 OID 19827)
-- Name: ensembl_uniprot mapping_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_uniprot ALTER COLUMN mapping_id SET DEFAULT nextval('ensembl_gifts.ensembl_uniprot_mapping_id_seq'::regclass);


--
-- TOC entry 2895 (class 2604 OID 19828)
-- Name: ensp_u_cigar ensp_u_cigar_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensp_u_cigar ALTER COLUMN ensp_u_cigar_id SET DEFAULT nextval('ensembl_gifts.ensp_u_cigar_ensp_u_cigar_id_seq'::regclass);


--
-- TOC entry 2896 (class 2604 OID 19829)
-- Name: isoform isoform_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.isoform ALTER COLUMN isoform_id SET DEFAULT nextval('ensembl_gifts.isoform_isoform_id_seq'::regclass);


--
-- TOC entry 2898 (class 2604 OID 19830)
-- Name: mapping_history mapping_history_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.mapping_history ALTER COLUMN mapping_history_id SET DEFAULT nextval('ensembl_gifts.mapping_history_mapping_history_id_seq'::regclass);


--
-- TOC entry 2899 (class 2604 OID 19831)
-- Name: pdb_ens pdb_ens_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.pdb_ens ALTER COLUMN pdb_ens_id SET DEFAULT nextval('ensembl_gifts.pdb_ens_pdb_ens_id_seq'::regclass);


--
-- TOC entry 2900 (class 2604 OID 19832)
-- Name: ptm ptm_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ptm ALTER COLUMN ptm_id SET DEFAULT nextval('ensembl_gifts.ptm_ptm_id_seq'::regclass);


--
-- TOC entry 2901 (class 2604 OID 19833)
-- Name: taxonomy_mapping taxonomy_mapping_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.taxonomy_mapping ALTER COLUMN taxonomy_mapping_id SET DEFAULT nextval('ensembl_gifts.taxonomy_mapping_taxonomy_mapping_id_seq'::regclass);


--
-- TOC entry 2905 (class 2604 OID 19834)
-- Name: ue_mapping_comment id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_comment ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.ue_mapping_comment_id_seq'::regclass);


--
-- TOC entry 2907 (class 2604 OID 19835)
-- Name: ue_mapping_label id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_label ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.ue_mapping_label_id_seq'::regclass);


--
-- TOC entry 2909 (class 2604 OID 19836)
-- Name: ue_mapping_status id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_status ALTER COLUMN id SET DEFAULT nextval('ensembl_gifts.ue_mapping_status_id_seq'::regclass);


--
-- TOC entry 2912 (class 2604 OID 19837)
-- Name: uniprot_entry uniprot_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry ALTER COLUMN uniprot_id SET DEFAULT nextval('ensembl_gifts.uniprot_entry_uniprot_id_seq'::regclass);


--
-- TOC entry 2914 (class 2604 OID 19838)
-- Name: uniprot_entry_history uniprot_entry_type_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry_history ALTER COLUMN uniprot_entry_type_id SET DEFAULT nextval('ensembl_gifts.uniprot_entry_history_uniprot_entry_type_id_seq'::regclass);


--
-- TOC entry 2916 (class 2604 OID 19839)
-- Name: uniprot_entry_type uniprot_entry_type_id; Type: DEFAULT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry_type ALTER COLUMN uniprot_entry_type_id SET DEFAULT nextval('ensembl_gifts.uniprot_entry_type_uniprot_entry_type_id_seq'::regclass);


--
-- TOC entry 2920 (class 2606 OID 19953)
-- Name: alignment idx_24996_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.alignment
    ADD CONSTRAINT idx_24996_primary PRIMARY KEY (alignment_id);


--
-- TOC entry 2925 (class 2606 OID 19955)
-- Name: alignment_run idx_25002_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.alignment_run
    ADD CONSTRAINT idx_25002_primary PRIMARY KEY (alignment_run_id);


--
-- TOC entry 2927 (class 2606 OID 19957)
-- Name: cv_entry_type idx_25010_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.cv_entry_type
    ADD CONSTRAINT idx_25010_primary PRIMARY KEY (id);


--
-- TOC entry 2929 (class 2606 OID 19959)
-- Name: cv_ue_label idx_25014_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.cv_ue_label
    ADD CONSTRAINT idx_25014_primary PRIMARY KEY (id);


--
-- TOC entry 2931 (class 2606 OID 19961)
-- Name: cv_ue_status idx_25017_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.cv_ue_status
    ADD CONSTRAINT idx_25017_primary PRIMARY KEY (id);


--
-- TOC entry 2934 (class 2606 OID 19963)
-- Name: domain idx_25022_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.domain
    ADD CONSTRAINT idx_25022_primary PRIMARY KEY (domain_id);


--
-- TOC entry 2936 (class 2606 OID 19965)
-- Name: ensembl_gene idx_25028_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_gene
    ADD CONSTRAINT idx_25028_primary PRIMARY KEY (gene_id);


--
-- TOC entry 2939 (class 2606 OID 19967)
-- Name: ensembl_species_history idx_25036_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_species_history
    ADD CONSTRAINT idx_25036_primary PRIMARY KEY (ensembl_species_history_id);


--
-- TOC entry 2943 (class 2606 OID 19969)
-- Name: ensembl_transcript idx_25043_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_transcript
    ADD CONSTRAINT idx_25043_primary PRIMARY KEY (transcript_id);


--
-- TOC entry 2946 (class 2606 OID 19971)
-- Name: ensembl_uniprot idx_25050_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_uniprot
    ADD CONSTRAINT idx_25050_primary PRIMARY KEY (mapping_id);


--
-- TOC entry 2949 (class 2606 OID 19973)
-- Name: ensp_u_cigar idx_25057_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensp_u_cigar
    ADD CONSTRAINT idx_25057_primary PRIMARY KEY (ensp_u_cigar_id);


--
-- TOC entry 2952 (class 2606 OID 19975)
-- Name: gene_history idx_25064_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.gene_history
    ADD CONSTRAINT idx_25064_primary PRIMARY KEY (ensembl_species_history_id, gene_id);


--
-- TOC entry 2954 (class 2606 OID 19977)
-- Name: isoform idx_25075_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.isoform
    ADD CONSTRAINT idx_25075_primary PRIMARY KEY (isoform_id);


--
-- TOC entry 2957 (class 2606 OID 19979)
-- Name: mapping_history idx_25081_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.mapping_history
    ADD CONSTRAINT idx_25081_primary PRIMARY KEY (mapping_history_id);


--
-- TOC entry 2959 (class 2606 OID 19981)
-- Name: pdb_ens idx_25088_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.pdb_ens
    ADD CONSTRAINT idx_25088_primary PRIMARY KEY (pdb_ens_id);


--
-- TOC entry 2961 (class 2606 OID 19983)
-- Name: ptm idx_25094_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ptm
    ADD CONSTRAINT idx_25094_primary PRIMARY KEY (ptm_id);


--
-- TOC entry 2964 (class 2606 OID 19985)
-- Name: taxonomy_mapping idx_25100_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.taxonomy_mapping
    ADD CONSTRAINT idx_25100_primary PRIMARY KEY (taxonomy_mapping_id);


--
-- TOC entry 2966 (class 2606 OID 19987)
-- Name: ue_mapping_comment idx_25111_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_comment
    ADD CONSTRAINT idx_25111_primary PRIMARY KEY (id);


--
-- TOC entry 2968 (class 2606 OID 19989)
-- Name: ue_mapping_label idx_25121_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_label
    ADD CONSTRAINT idx_25121_primary PRIMARY KEY (id);


--
-- TOC entry 2970 (class 2606 OID 19991)
-- Name: ue_mapping_status idx_25128_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ue_mapping_status
    ADD CONSTRAINT idx_25128_primary PRIMARY KEY (id);


--
-- TOC entry 2972 (class 2606 OID 19993)
-- Name: uniprot_entry idx_25135_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry
    ADD CONSTRAINT idx_25135_primary PRIMARY KEY (uniprot_id);


--
-- TOC entry 2974 (class 2606 OID 20116)
-- Name: uniprot_entry_history idx_25143_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry_history
    ADD CONSTRAINT idx_25143_primary PRIMARY KEY (uniprot_entry_type_id, release_version);


--
-- TOC entry 2976 (class 2606 OID 19997)
-- Name: uniprot_entry_type idx_25150_primary; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry_type
    ADD CONSTRAINT idx_25150_primary PRIMARY KEY (uniprot_entry_type_id);


--
-- TOC entry 2979 (class 2606 OID 20103)
-- Name: transcript_history transcript_history_pkey; Type: CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.transcript_history
    ADD CONSTRAINT transcript_history_pkey PRIMARY KEY (ensembl_species_history_id, transcript_id);


--
-- TOC entry 2917 (class 1259 OID 19998)
-- Name: idx_24996_alignment_run_id; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_24996_alignment_run_id ON ensembl_gifts.alignment USING btree (alignment_run_id);


--
-- TOC entry 2918 (class 1259 OID 19999)
-- Name: idx_24996_mapping_id; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_24996_mapping_id ON ensembl_gifts.alignment USING btree (mapping_id);


--
-- TOC entry 2921 (class 1259 OID 20000)
-- Name: idx_24996_transcript_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_24996_transcript_id_idx ON ensembl_gifts.alignment USING btree (transcript_id);


--
-- TOC entry 2922 (class 1259 OID 20001)
-- Name: idx_24996_uniprot_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_24996_uniprot_id_idx ON ensembl_gifts.alignment USING btree (uniprot_id);


--
-- TOC entry 2923 (class 1259 OID 20002)
-- Name: idx_25002_mapping_history_id; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_25002_mapping_history_id ON ensembl_gifts.alignment_run USING btree (mapping_history_id);


--
-- TOC entry 2932 (class 1259 OID 20003)
-- Name: idx_25022_isoform_id; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_25022_isoform_id ON ensembl_gifts.domain USING btree (isoform_id);


--
-- TOC entry 2940 (class 1259 OID 20114)
-- Name: idx_25043_enst_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE UNIQUE INDEX idx_25043_enst_id_idx ON ensembl_gifts.ensembl_transcript USING btree (enst_id);


--
-- TOC entry 2941 (class 1259 OID 20005)
-- Name: idx_25043_gene_id_idx; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_25043_gene_id_idx ON ensembl_gifts.ensembl_transcript USING btree (gene_id);


--
-- TOC entry 2944 (class 1259 OID 20006)
-- Name: idx_25050_ensembl_transcript_idx; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_25050_ensembl_transcript_idx ON ensembl_gifts.ensembl_uniprot USING btree (transcript_id);


--
-- TOC entry 2947 (class 1259 OID 20007)
-- Name: idx_25050_uniprot_idx_idx; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_25050_uniprot_idx_idx ON ensembl_gifts.ensembl_uniprot USING btree (uniprot_id);


--
-- TOC entry 2950 (class 1259 OID 20008)
-- Name: idx_25064_gh_g_id; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_25064_gh_g_id ON ensembl_gifts.gene_history USING btree (gene_id);


--
-- TOC entry 2955 (class 1259 OID 20009)
-- Name: idx_25075_uniform_isoform_idx; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_25075_uniform_isoform_idx ON ensembl_gifts.isoform USING btree (uniprot_id);


--
-- TOC entry 2962 (class 1259 OID 20010)
-- Name: idx_25094_ptm_domain; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_25094_ptm_domain ON ensembl_gifts.ptm USING btree (domain_id);


--
-- TOC entry 2977 (class 1259 OID 20011)
-- Name: idx_25150_uniprot_entry_version_uniprot_entry_fk; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE INDEX idx_25150_uniprot_entry_version_uniprot_entry_fk ON ensembl_gifts.uniprot_entry_type USING btree (uniprot_id);


--
-- TOC entry 2937 (class 1259 OID 20012)
-- Name: idx_stable_id_gene; Type: INDEX; Schema: ensembl_gifts; Owner: -
--

CREATE UNIQUE INDEX idx_stable_id_gene ON ensembl_gifts.ensembl_gene USING btree (ensg_id);


--
-- TOC entry 2995 (class 2620 OID 20013)
-- Name: mapping_history on_update_current_timestamp; Type: TRIGGER; Schema: ensembl_gifts; Owner: -
--

CREATE TRIGGER on_update_current_timestamp BEFORE UPDATE ON ensembl_gifts.mapping_history FOR EACH ROW EXECUTE PROCEDURE ensembl_gifts.on_update_current_timestamp_mapping_history();


--
-- TOC entry 2980 (class 2606 OID 20014)
-- Name: alignment alignment_run_id; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.alignment
    ADD CONSTRAINT alignment_run_id FOREIGN KEY (alignment_run_id) REFERENCES ensembl_gifts.alignment_run(alignment_run_id);


--
-- TOC entry 2990 (class 2606 OID 20019)
-- Name: ptm domain_id; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ptm
    ADD CONSTRAINT domain_id FOREIGN KEY (domain_id) REFERENCES ensembl_gifts.domain(domain_id);


--
-- TOC entry 2986 (class 2606 OID 20024)
-- Name: ensembl_uniprot ensembl_transcript_idx; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_uniprot
    ADD CONSTRAINT ensembl_transcript_idx FOREIGN KEY (transcript_id) REFERENCES ensembl_gifts.ensembl_transcript(transcript_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2987 (class 2606 OID 20029)
-- Name: ensembl_uniprot ensembl_uniprot_uniprot_entry_version_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_uniprot
    ADD CONSTRAINT ensembl_uniprot_uniprot_entry_version_fk FOREIGN KEY (uniprot_id) REFERENCES ensembl_gifts.uniprot_entry_type(uniprot_entry_type_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2985 (class 2606 OID 20034)
-- Name: ensembl_transcript g_id; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.ensembl_transcript
    ADD CONSTRAINT g_id FOREIGN KEY (gene_id) REFERENCES ensembl_gifts.ensembl_gene(gene_id);


--
-- TOC entry 2988 (class 2606 OID 20039)
-- Name: gene_history gh_g_id; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.gene_history
    ADD CONSTRAINT gh_g_id FOREIGN KEY (gene_id) REFERENCES ensembl_gifts.ensembl_gene(gene_id);


--
-- TOC entry 2989 (class 2606 OID 20044)
-- Name: gene_history gh_h_id; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.gene_history
    ADD CONSTRAINT gh_h_id FOREIGN KEY (ensembl_species_history_id) REFERENCES ensembl_gifts.ensembl_species_history(ensembl_species_history_id);


--
-- TOC entry 2984 (class 2606 OID 20049)
-- Name: domain isoform_idx; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.domain
    ADD CONSTRAINT isoform_idx FOREIGN KEY (isoform_id) REFERENCES ensembl_gifts.isoform(isoform_id);


--
-- TOC entry 2983 (class 2606 OID 20054)
-- Name: alignment_run mapping_history_id; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.alignment_run
    ADD CONSTRAINT mapping_history_id FOREIGN KEY (mapping_history_id) REFERENCES ensembl_gifts.mapping_history(mapping_history_id);


--
-- TOC entry 2981 (class 2606 OID 20059)
-- Name: alignment mapping_id; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.alignment
    ADD CONSTRAINT mapping_id FOREIGN KEY (mapping_id) REFERENCES ensembl_gifts.ensembl_uniprot(mapping_id);


--
-- TOC entry 2994 (class 2606 OID 20109)
-- Name: transcript_history none; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.transcript_history
    ADD CONSTRAINT "none" FOREIGN KEY (transcript_id) REFERENCES ensembl_gifts.ensembl_transcript(transcript_id);


--
-- TOC entry 2993 (class 2606 OID 20104)
-- Name: transcript_history transcript_history_ensembl_species_history_id_fkey; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.transcript_history
    ADD CONSTRAINT transcript_history_ensembl_species_history_id_fkey FOREIGN KEY (ensembl_species_history_id) REFERENCES ensembl_gifts.ensembl_species_history(ensembl_species_history_id);


--
-- TOC entry 2982 (class 2606 OID 20064)
-- Name: alignment transcript_id_idx; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.alignment
    ADD CONSTRAINT transcript_id_idx FOREIGN KEY (transcript_id) REFERENCES ensembl_gifts.ensembl_transcript(transcript_id);


--
-- TOC entry 2991 (class 2606 OID 20117)
-- Name: uniprot_entry_history uniprot_entry_history_uniprot_entry_version_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry_history
    ADD CONSTRAINT uniprot_entry_history_uniprot_entry_version_fk FOREIGN KEY (uniprot_entry_type_id) REFERENCES ensembl_gifts.uniprot_entry_type(uniprot_entry_type_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2992 (class 2606 OID 20074)
-- Name: uniprot_entry_type uniprot_entry_version_uniprot_entry_fk; Type: FK CONSTRAINT; Schema: ensembl_gifts; Owner: -
--

ALTER TABLE ONLY ensembl_gifts.uniprot_entry_type
    ADD CONSTRAINT uniprot_entry_version_uniprot_entry_fk FOREIGN KEY (uniprot_id) REFERENCES ensembl_gifts.uniprot_entry(uniprot_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


-- Completed on 2018-05-24 11:33:55 BST

--
-- PostgreSQL database dump complete
--

