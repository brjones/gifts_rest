BEGIN;
--
-- Create model Alignment
--
CREATE TABLE "alignment" ("alignment_id" bigserial NOT NULL PRIMARY KEY, "uniprot_id" bigint NULL, "score1" double precision NULL, "report" varchar(300) NULL, "is_current" boolean NULL, "score2" double precision NULL);
--
-- Create model AlignmentRun
--
CREATE TABLE "alignment_run" ("alignment_run_id" bigserial NOT NULL PRIMARY KEY, "userstamp" varchar(30) NULL, "time_run" timestamp with time zone NULL, "score1_type" varchar(30) NULL, "report_type" varchar(30) NULL, "pipeline_name" varchar(30) NOT NULL, "pipeline_comment" varchar(300) NOT NULL, "ensembl_release" bigint NOT NULL, "uniprot_file_swissprot" varchar(300) NULL, "uniprot_file_isoform" varchar(300) NULL, "uniprot_dir_trembl" varchar(300) NULL, "logfile_dir" varchar(300) NULL, "pipeline_script" varchar(300) NOT NULL, "score2_type" varchar(30) NULL);
--
-- Create model CvEntryType
--
CREATE TABLE "cv_entry_type" ("id" bigint NOT NULL PRIMARY KEY, "description" varchar(20) NULL);
--
-- Create model CvUeLabel
--
CREATE TABLE "cv_ue_label" ("id" bigint NOT NULL PRIMARY KEY, "description" varchar(20) NOT NULL);
--
-- Create model CvUeStatus
--
CREATE TABLE "cv_ue_status" ("id" bigint NOT NULL PRIMARY KEY, "description" varchar(20) NOT NULL);
--
-- Create model Domain
--
CREATE TABLE "domain" ("domain_id" bigserial NOT NULL PRIMARY KEY, "start" bigint NULL, "end" bigint NULL, "description" varchar(45) NULL);
--
-- Create model EnsemblGene
--
CREATE TABLE "ensembl_gene" ("gene_id" bigserial NOT NULL PRIMARY KEY, "ensg_id" varchar(30) NULL UNIQUE, "gene_name" varchar(30) NULL, "chromosome" varchar(50) NULL, "region_accession" varchar(50) NULL, "mod_id" varchar(30) NULL, "deleted" boolean NULL, "seq_region_start" bigint NULL, "seq_region_end" bigint NULL, "seq_region_strand" bigint NULL, "biotype" varchar(40) NULL, "time_loaded" timestamp with time zone NULL);
--
-- Create model EnsemblSpeciesHistory
--
CREATE TABLE "ensembl_species_history" ("ensembl_species_history_id" bigserial NOT NULL PRIMARY KEY, "species" varchar(30) NULL, "assembly_accession" varchar(30) NULL, "ensembl_tax_id" bigint NULL, "ensembl_release" bigint NULL, "status" varchar(30) NULL, "time_loaded" timestamp with time zone NULL);
--
-- Create model EnsemblTranscript
--
CREATE TABLE "ensembl_transcript" ("transcript_id" bigserial NOT NULL PRIMARY KEY, "enst_id" varchar(30) NULL, "enst_version" smallint NULL, "ccds_id" varchar(30) NULL, "uniparc_accession" varchar(30) NULL, "biotype" varchar(40) NULL, "deleted" boolean NULL, "seq_region_start" bigint NULL, "seq_region_end" bigint NULL, "supporting_evidence" varchar(45) NULL, "userstamp" varchar(30) NULL, "time_loaded" timestamp with time zone NULL);
--
-- Create model EnsemblUniprot
--
CREATE TABLE "ensembl_uniprot" ("mapping_id" bigserial NOT NULL PRIMARY KEY, "userstamp" varchar(30) NULL, "timestamp" timestamp with time zone NULL, "mapping_history_id" bigint NULL, "sp_ensembl_mapping_type" varchar(50) NULL, "uniprot_entry_version" integer NULL, "uniprot_ensembl_derived" smallint NULL);
--
-- Create model EnspUCigar
--
CREATE TABLE "ensp_u_cigar" ("ensp_u_cigar_id" bigserial NOT NULL PRIMARY KEY, "cigarplus" text NULL, "mdz" text NULL, "uniprot_acc" varchar(30) NOT NULL, "uniprot_seq_version" smallint NOT NULL, "ensp_id" varchar(30) NOT NULL);
--
-- Create model Isoform
--
CREATE TABLE "isoform" ("isoform_id" bigserial NOT NULL PRIMARY KEY, "uniprot_id" bigint NULL, "accession" varchar(30) NULL, "sequence" varchar(200) NULL, "uniparc_accession" varchar(30) NULL, "embl_acc" varchar(30) NULL);
--
-- Create model MappingHistory
--
CREATE TABLE "mapping_history" ("mapping_history_id" bigserial NOT NULL PRIMARY KEY, "ensembl_species_history_id" bigint NULL, "time_mapped" timestamp with time zone NOT NULL, "entries_mapped" bigint NULL, "entries_unmapped" bigint NULL, "uniprot_release" varchar(7) NULL, "uniprot_taxid" bigint NULL, "status" varchar(20) NULL);
--
-- Create model PdbEns
--
CREATE TABLE "pdb_ens" ("pdb_ens_id" bigserial NOT NULL PRIMARY KEY, "pdb_acc" varchar(45) NOT NULL, "pdb_release" varchar(11) NOT NULL, "uniprot_acc" varchar(30) NOT NULL, "enst_id" varchar(30) NOT NULL, "enst_version" bigint NULL, "ensp_id" varchar(30) NOT NULL, "ensp_start" bigint NULL, "ensp_end" bigint NULL, "pdb_start" bigint NULL, "pdb_end" bigint NULL, "pdb_chain" varchar(6) NOT NULL);
--
-- Create model Ptm
--
CREATE TABLE "ptm" ("ptm_id" bigserial NOT NULL PRIMARY KEY, "description" varchar(45) NULL, "start" bigint NULL, "end" bigint NULL);
--
-- Create model TaxonomyMapping
--
CREATE TABLE "taxonomy_mapping" ("taxonomy_mapping_id" bigserial NOT NULL PRIMARY KEY, "ensembl_tax_id" bigint NULL, "uniprot_tax_id" bigint NULL);
--
-- Create model TempMap
--
CREATE TABLE "temp_map" ("id" serial NOT NULL PRIMARY KEY, "uniprot_id" bigint NOT NULL, "uniprot_entry_version_id" bigint NOT NULL);
--
-- Create model UeMappingComment
--
CREATE TABLE "ue_mapping_comment" ("id" bigserial NOT NULL PRIMARY KEY, "uniprot_acc" varchar(30) NOT NULL, "enst_id" varchar(30) NOT NULL, "time_stamp" timestamp with time zone NOT NULL, "user_stamp" varchar(20) NOT NULL, "comment" text NOT NULL);
--
-- Create model UeMappingLabel
--
CREATE TABLE "ue_mapping_label" ("id" bigserial NOT NULL PRIMARY KEY, "uniprot_acc" varchar(30) NOT NULL, "enst_id" varchar(30) NOT NULL, "time_stamp" timestamp with time zone NOT NULL, "user_stamp" varchar(20) NOT NULL, "label" bigint NOT NULL);
--
-- Create model UeMappingStatus
--
CREATE TABLE "ue_mapping_status" ("id" bigserial NOT NULL PRIMARY KEY, "uniprot_acc" varchar(30) NOT NULL, "enst_id" varchar(30) NOT NULL, "time_stamp" timestamp with time zone NOT NULL, "user_stamp" varchar(20) NOT NULL, "status" bigint NOT NULL);
--
-- Create model UniprotEntry
--
CREATE TABLE "uniprot_entry" ("uniprot_id" bigserial NOT NULL PRIMARY KEY, "uniprot_acc" varchar(30) NULL, "uniprot_tax_id" bigint NULL, "userstamp" varchar(30) NULL, "timestamp" timestamp with time zone NULL, "sequence_version" smallint NULL, "upi" varchar(13) NULL, "md5" varchar(32) NULL);
--
-- Create model UniprotEntryVersion
--
CREATE TABLE "uniprot_entry_version" ("uniprot_entry_version_id" bigserial NOT NULL PRIMARY KEY, "protein_existence_id" bigint NULL, "ensembl_derived" boolean NULL, "is_isoform" boolean NULL, "entry_type" boolean NULL, "userstamp" varchar(30) NULL, "timestamp" timestamp with time zone NULL, "entry_version" bigint NULL, "is_canonical" bigint NULL, "canonical_accession" varchar(30) NULL);
--
-- Create model GeneHistory
--
CREATE TABLE "gene_history" ("ensembl_species_history_id" bigint NOT NULL PRIMARY KEY);
--
-- Create model UniprotEntryHistory
--
CREATE TABLE "uniprot_entry_history" ("uniprot_entry_version_id_id" bigint NOT NULL PRIMARY KEY, "release_version" varchar(30) NOT NULL);
CREATE INDEX "ensembl_gene_ensg_id_92a92aa7_like" ON "ensembl_gene" ("ensg_id" varchar_pattern_ops);
ALTER TABLE "gene_history" ADD CONSTRAINT "gene_history_ensembl_species_hist_bc305d6f_fk_ensembl_s" FOREIGN KEY ("ensembl_species_history_id") REFERENCES "ensembl_species_history" ("ensembl_species_history_id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "uniprot_entry_history" ADD CONSTRAINT "uniprot_entry_histor_uniprot_entry_versio_b1a47f0a_fk_uniprot_e" FOREIGN KEY ("uniprot_entry_version_id_id") REFERENCES "uniprot_entry_version" ("uniprot_entry_version_id") DEFERRABLE INITIALLY DEFERRED;
COMMIT;
