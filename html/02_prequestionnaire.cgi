#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Pre-questionnaire screen
#
#   2020-08-05 by OGAWA, Y.

use lib qw(pm .);


use strict;
use warnings;
use utf8;
use CGI;
use HTML::Template;
use CGI::Carp( 'fatalsToBrowser' );

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

my $tmpl = &Util::load_html_tmpl('02_prequestionnaire.tmpl' );


my $user = &Util::form_str_utf8($q, 'user');
$tmpl->param( user => "$user" ); 


my @prefectures;

my $prefecture = &Info::get_all_prefecture_file_path;
open (FILE, "<", $prefecture) or die "Failed to open $prefecture\n"; 

while (my $line = <FILE>) {
    $line = &Encode::decode($Data_Charset, $line);
    $line =~ s/[\r\n]+\z//;
    push @prefectures, $line;
}

close (FILE);


push my @prefectures_choices, '<option value="">選択してください</option>';

foreach (@prefectures) {
    push @prefectures_choices, '<option value="'.$_.'">'.$_.'</option>';
}


$tmpl->param( prefectures_choices => "@prefectures_choices" ); 


print $q->header;
print &Encode::encode('utf-8', $tmpl->output);
