#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Login screen
#
#   2020-08-05 by OGAWA, Y.

use lib qw(pm .);

use strict;
use warnings;
use utf8;

use CGI;
use HTML::Template;

use CGI::Carp( 'fatalsToBrowser' );


use Info;
use Util;
use Quiz;
use Par;

my $q = CGI->new;
$q->charset( 'UTF-8' );


my $tmpl = &Util::load_html_tmpl('00_login_01.tmpl' );

# Get the number of questions for each test
my $pre_test_answer_file = &Info::get_all_pre_choices_answer_file_path;
my ($pre_question, $mp3_all, $correct_answer_all)
 = &Quiz::get_n_question_and_answer_lists($pre_test_answer_file);

$tmpl->param( pre_question => $pre_question ); 


my $m_test_answer_file = &Info::get_all_m_choices_answer_file_path;
(my $m_question, $mp3_all, $correct_answer_all)
 = &Quiz::get_n_question_and_answer_lists($m_test_answer_file);

$tmpl->param( m_question => $m_question ); 

my $post_test_answer_file = &Info::get_all_post_choices_answer_file_path;
(my $post_question, $mp3_all, $correct_answer_all)
 = &Quiz::get_n_question_and_answer_lists($post_test_answer_file);

$tmpl->param( post_question => $post_question ); 

my $d_test_answer_file = &Info::get_all_d_choices_answer_file_path;
(my $d_question, $mp3_all, $correct_answer_all)
 = &Quiz::get_n_question_and_answer_lists($d_test_answer_file);

$tmpl->param( d_question => $d_question ); 

print $q->header;
print &Encode::encode('utf-8', $tmpl->output);