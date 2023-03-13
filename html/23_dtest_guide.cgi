#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Delayed test guide screen
#
#   2020-08-05 by OGAWA, Y.

use lib qw(pm .);

use strict;
use warnings;
use CGI;
use HTML::Template;
use CGI::Carp( 'fatalsToBrowser' );

use Info;
use Util;
use Quiz;
use Time::Piece;

use Encode;
my $Data_Charset = 'utf-8';

my $q = CGI->new;
$q->charset( 'UTF-8' );

# If you came to this page without logging in
unless ($q->param( 'user' )){  # No user name → Not logged in
	# Display message and exit
	my $tmpl = &Util::load_html_tmpl('not_logged_in_message.tmpl' );
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; # Terminate all programs
}

my $user = &Util::form_str_utf8($q, 'user');


my $tmpl = &Util::load_html_tmpl('23_dtest_guide.tmpl' );
$tmpl->param( user => "$user" ); 

my $test_answer_file = &Info::get_all_post_choices_answer_file_path;
my ($n_question, $mp3_all, $correct_answer_all)
 = &Quiz::get_n_question_and_answer_lists($test_answer_file);

$tmpl->param( n_question => $n_question ); 

print $q->header;
print &Encode::encode('utf-8', $tmpl->output);
