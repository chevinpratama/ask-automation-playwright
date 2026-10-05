detail_project = {
    "project_name": "Automation ACS Surety",
    "project_code": "000000",
    "project_type": "New",
    "core_noncore": "core",
    "platform": "Windows 11 64 Bit",
    "browser": "Chrome"
}
# ini bagian yang dapat diganti sesuai project kalian
testcase_data = {
     # -------Akseptasi Surety----------------#
    "Akseptasi_SuretyBond": {
        "module_name": "Akseptasi",
        "testcase_id": "TC-1",
        "testcase_name": "Input akseptasi baru SuretyBond Jenis Jaminan Penawaran",
        "jenis_test": "Positive",
        "expected_result": "Sistem berhasil membuat Polis Surety dengan Jenis jaminan Penawaran dan data tersimpan di ACS.",
        "actual_result": "Sistem berhasil membuat Polis Surety dengan Jenis jaminan Penawaran dan data tersimpan di ACS."

    },
    # -------Endorsement Surety----------------#
    "Endorsement_NonFinancial": {
        "module_name": "Endorsement",
        "testcase_id": "TC-2",
        "testcase_name": "Endorsement NonFinancial SuretyBond Jenis Jaminan Penawaran",
        "jenis_test": "Positive",
        "expected_result": "Sistem berhasil endorsement non financial Polis Surety dengan Jenis jaminan Penawaran dan data tersimpan di ACS.",
        "actual_result": "Sistem berhasil endorsement non financial Polis Surety dengan Jenis jaminan Penawaran dan data tersimpan di ACS."
    },

    # -------Endorsement Surety----------------#
    "Endorsement_Financial": {
        "module_name": "Endorsement",
        "testcase_id": "TC-3",
        "testcase_name": "Endorsement Financial SuretyBond Jenis Jaminan Penawaran",
        "jenis_test": "Positive",
        "expected_result": "Sistem berhasil endorsement financial Polis Surety dengan Jenis jaminan Penawaran dan data tersimpan di ACS.",
        "actual_result": "Sistem berhasil endorsement financial Polis Surety dengan Jenis jaminan Penawaran dan data tersimpan di ACS."
    },

    # -------Endorsement Surety----------------#
    "Endorsement_Cancellation": {
        "module_name": "Endorsement",
        "testcase_id": "TC-4",
        "testcase_name": "Endorsement Cancellation SuretyBond Jenis Jaminan Penawaran",
        "jenis_test": "Positive",
        "expected_result": "Sistem berhasil endorsement cancellation Polis Surety dengan Jenis jaminan Penawaran dan data tersimpan di ACS.",
        "actual_result": "Sistem berhasil endorsement cancellation Polis Surety dengan Jenis jaminan Penawaran dan data tersimpan di ACS."
    },

    # -------Claim Surety-----------------#
    "Klaim_Surety_Setuju": {
        "module_name": "Claim",
        "testcase_id": "TC-1",
        "testcase_name": "Input Registrasi Klaim - SuretyBond",
        "jenis_test": "Positive",
        "expected_result": "Sistem berhasil melakukan registrasi klaim sampai setuju",
        "actual_result": "Sistem berhasil melakukan registrasi klaim sampai setuju"
    },

    # -------Claim Surety Endorse Lebih Bayar-----------------#
    "Klaim_Surety_LebihBayar": {
        "module_name": "Claim",
        "testcase_id": "TC-2",
        "testcase_name": "Input Endorsement Klaim Lebih Bayar",
        "jenis_test": "Positive",
        "expected_result": "Sistem berhasil melakukan endorsement klaim lebih bayar",
        "actual_result": "Sistem berhasil melakukan endorsement klaim lebih bayar"
    },
    
    # -------Akseptasi Persetujuan Prinsip 1701 (Agen Perseorangan)-----------------#
    "Akseptasi_1701_AgenPerseorangan": {
        "module_name": "Akseptasi",
        "testcase_id": "TC-3.1",
        "testcase_name": "Input akseptasi baru Persetujuan Prinsip Jenis Jaminan 1701",
        "jenis_test": "Positive",
        "precondition": (
            "1. User akses dengan crendtial yang valid\n"
        ),
        "tester_name": "Fathurrahman Al Farizi",
        "expected_result": "Sistem berhasil membuat Polis PP dengan Jenis jaminan 1701- dan data tersimpan di ACS.",
        "actual_result": "Sistem berhasil membuat Polis PP dengan Jenis jaminan 1701- dan data tersimpan di ACS."
    },


    # -------Akseptasi Persetujuan Prinsip 1704 (Agen Perseorangan)-----------------#
    "Akseptasi_1704_AgenPerseorangan": {
        "module_name": "Akseptasi",
        "testcase_id": "TC-3.2",
        "testcase_name": "Input akseptasi baru Persetujuan Prinsip Jenis Jaminan 1704",
        "jenis_test": "Positive",
        "precondition": (
            "1. User akses dengan crendtial yang valid\n"
        ),
        "tester_name": "Fathurrahman Al Farizi",
        "expected_result": "Sistem berhasil membuat Polis PP dengan Jenis jaminan 1704- dan data tersimpan di ACS.",
        "actual_result": "Sistem berhasil membuat Polis PP dengan Jenis jaminan 1704- dan data tersimpan di ACS."
    },


}
