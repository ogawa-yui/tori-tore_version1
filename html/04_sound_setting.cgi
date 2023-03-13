#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Questionnaire responses writing & sound source playback setting screen
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

my $tmpl = &Util::load_html_tmpl('04_sound_setting.tmpl' );

my $user = &Util::form_str_utf8($q, 'user');
$tmpl->param( user => "$user" ); 

unless ($q->param ( 'a1' )){ # If you have not access from the questionnaire screen 
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; # Terminate all programs
}

my $a1 = &Util::form_str_utf8($q, 'a1' );
my $confirm = &Util::form_str_utf8($q, 'confirm' );
my $a2_1 = &Util::form_str_utf8($q, 'a2_1' );
my $a2_2 = &Util::form_str_utf8($q, 'a2_2' );
my $a3 = &Util::form_str_utf8($q, 'a3' );
my $a4 = &Util::form_str_utf8($q, 'a4' );
my $a5 = &Util::form_str_utf8($q, 'a5' );
my $a6 = &Util::form_str_utf8($q, 'a6' );
my $a7 = &Util::form_str_utf8($q, 'a7' );
my $a8_1_or_0 = &Util::form_str_utf8($q, 'a8_1_or_0' ); # Check box
my $a8_7 = &Util::form_str_utf8($q, 'a8_7' ); # Other
my $a9_1 = &Util::form_str_utf8($q, 'a9_1' );
my $a9_2 = &Util::form_str_utf8($q, 'a9_2' );
my $a9_3 = &Util::form_str_utf8($q, 'a9_3' );
my $a9_4 = &Util::form_str_utf8($q, 'a9_4' );

my ($day, $date, $time) = &Util::get_day_date_time;

# Write questionnaire responses
my $response_log_file = &Info::get_all_prequestionnaire_responses_file_path;
open (FILE, ">>", $response_log_file) or die "Failed to open $response_log_file\n";
print FILE &Encode::encode('utf-8',
 "$date\t$time\t$ENV{REMOTE_ADDR}\t$ENV{HTTP_USER_AGENT}\t$user\t$confirm\t$a1\t$a2_1\t$a2_2\t$a3\t$a4\t$a5\t$a6\t$a7\t$a8_1_or_0\t$a8_7\t$a9_1\t$a9_2\t$a9_3\t$a9_4\n");
close (FILE); 


print $q->header;
print &Encode::encode('utf-8', $tmpl->output);
