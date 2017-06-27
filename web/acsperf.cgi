#!/usr/bin/perl -w

use strict;
use warnings;
use File::Copy;
use File::Compare;
use LWP::Simple;

my $CWMP_IP = "192.168.1.39";
my $img_dir = "/home/quyenlv/oneweb/backend/images";
my $BENCH2GRAPH = "/home/quyenlv/Autobench/bench2graph";

#
# Get number of CWMP core processors
#

sub
get_core_num
{
    my ($ip) = @_;
    my $core_num = 0;

    my $url = "http://$ip:19999".
        "/api/v1/data?chart=apps.processes".
        "&after=-1&before=0".
        "&group=average&options=seconds&format=csv";

    my ($apps_name, $apps_procs) = split "\n", get $url;

    my @apps = split ",", $apps_name;
    my @procs = split ",", $apps_procs;

    my %hash;
    @hash{@apps} = @procs;

    $core_num = $hash{nodejs} if (exists $hash{nodejs});

    return $core_num;
}


#
# Main
#

my $raw_data = `find /tmp/tms_* -path \*result/raw/data 2>/dev/null | sort -r | head -1`;
my $temp_data = "/tmp/.testACSdata";

# Remove trailing new feed line
$raw_data =~ s/\R//g;

# Skip generate testing result if there is no change
exit 0 if (compare ($raw_data, $temp_data) == 0);

copy ($raw_data, $temp_data) or die "Copy failed: $!";

my $core_num = get_core_num($CWMP_IP);

system ("echo 'Session Rate \(${core_num} core\)' | $BENCH2GRAPH $raw_data ".
		"$img_dir/sess_rate.png 1 9 10 11 12 > /dev/null 2>&1");

system ("echo 'Concurrent Rate \(${core_num} core\)' | $BENCH2GRAPH $raw_data ".
		"$img_dir/concur_rate.png 1 13 > /dev/null 2>&1");

system ("echo 'Error Rate \(${core_num} core\)' | $BENCH2GRAPH $raw_data ".
		"$img_dir/error_rate.png 1 17 18 19 20 21 > /dev/null 2>&1");

system ("echo 'Time Rate \(${core_num} core\)' | $BENCH2GRAPH $raw_data ".
		"$img_dir/time_rate.png 1 14 15 > /dev/null 2>&1");

